import pytest
from unittest.mock import MagicMock, patch
import sys
import importlib

# --- Mock Infrastructure (Copied/Adapted from test_products_tab.py) ---
class MockFrame:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.winfo_children_val = []
    def grid(self, **kwargs): pass
    def pack(self, **kwargs): pass
    def place(self, **kwargs): pass
    def destroy(self): pass
    def bind(self, *args, **kwargs): pass
    def winfo_id(self): return 12345
    def winfo_children(self): return self.winfo_children_val
    def columnconfigure(self, *args, **kwargs): pass
    def rowconfigure(self, *args, **kwargs): pass

@pytest.fixture
def mock_tk_env():
    mock_tk = MagicMock()
    mock_tk.Frame = MockFrame
    mock_tk.LabelFrame = MockFrame
    mock_tk.Toplevel = MockFrame 
    mock_tk.Tk = MockFrame
    mock_tk.Entry.side_effect = lambda *args, **kwargs: MagicMock()
    
    modules = {
        'tkinter': mock_tk,
        'tkinter.ttk': MagicMock(),
        'tkinter.messagebox': MagicMock(),
        'tkinter.filedialog': MagicMock()
    }
    
    with patch.dict(sys.modules, modules):
        # Must reload to ensure mocks are picked up
        import gui.forms.product_form
        importlib.reload(gui.forms.product_form)
        yield
        
    # Cleanup: Reload to restore real module state
    import gui.forms.product_form
    importlib.reload(gui.forms.product_form)

@pytest.fixture
def form(mock_tk_env):
    with patch('gui.forms.product_form.APIClient'):
        from gui.forms.product_form import ProductForm
        parent = MagicMock()
        # Initialize form with just parent
        form = ProductForm(parent)
        # Initialize entry_weight.get() to return empty string so auto-calc works
        form.entry_weight.get.return_value = ""
        return form

# --- Helper Functions ---
def set_val(mock_entry, value):
    """Set the return value of .get() for a mock entry"""
    mock_entry.get.return_value = str(value)

def setup_bom(form, **kwargs):
    """
    Helper to set multiple BOM fields at once.
    Default for unspecified fields is 0 or 1 where appropriate.
    """
    # defaults
    defaults = {
        'wax_g': 0, 'wax_rate': 0,
        'frag_g': 0, 'frag_rate': 0,
        'wick_qty': 1, 'wick_rate': 0,
        'cont1_qty': 1, 'cont1_rate': 0, # Glass
        'cont2_g': 0, 'cont2_rate': 0,   # Gypsum
        'labor_min': 0, 'labor_rate': 0,
        'box_qty': 1, 'box_rate': 0,
        'wrap': 0, 'biz_card': 0
    }
    # update with kwargs
    params = {**defaults, **kwargs}
    
    set_val(form.entry_wax_g, params['wax_g'])
    set_val(form.entry_wax_rate, params['wax_rate'])
    set_val(form.entry_fragrance_g, params['frag_g'])
    set_val(form.entry_frag_rate, params['frag_rate'])
    
    set_val(form.entry_wick_qty, params['wick_qty'])
    set_val(form.entry_wick_rate, params['wick_rate'])
    
    set_val(form.entry_container_qty, params['cont1_qty'])
    set_val(form.entry_container_rate, params['cont1_rate'])
    
    set_val(form.entry_second_container_g, params['cont2_g'])
    set_val(form.entry_second_container_rate, params['cont2_rate'])
    
    set_val(form.entry_labor_time, params['labor_min'])
    set_val(form.entry_labor_rate, params['labor_rate'])
    
    set_val(form.entry_box_qty, params['box_qty'])
    set_val(form.entry_box, params['box_rate'])
    set_val(form.entry_wrap, params['wrap'])
    set_val(form.entry_biz_card, params['biz_card'])


# --- Tests ---

def test_calc_basic_wax_fragrance(form):
    """
    Test 1: Simple Wax + Fragrance calculation.
    Wax: 100g @ $10/kg = $1.00
    Frag: 10g @ $100/kg = $1.00
    Total: $2.00
    """
    setup_bom(form, 
              wax_g=100, wax_rate=10, 
              frag_g=10, frag_rate=100)
    
    cost = form.calculate_cogs()
    assert cost == pytest.approx(2.00, 0.01)

def test_calc_simple_unit_container(form):
    """
    Test 2: Glass Container (Unit based).
    Qty: 2 @ $1.50/unit = $3.00
    """
    setup_bom(form, cont1_qty=2, cont1_rate=1.50)
    cost = form.calculate_cogs()
    assert cost == pytest.approx(3.00, 0.01)

def test_calc_simple_weight_container(form):
    """
    Test 3: Gypsum Container (Weight based).
    Weight: 200g @ $5.00/kg = $1.00
    """
    setup_bom(form, cont2_g=200, cont2_rate=5.00)
    cost = form.calculate_cogs()
    assert cost == pytest.approx(1.00, 0.01)

def test_calc_dual_containers(form):
    """
    Test 4: Both Containers.
    Glass: 1 @ $2.00 = $2.00
    Gypsum: 100g @ $10.00/kg = $1.00
    Total: $3.00
    """
    setup_bom(form, 
              cont1_qty=1, cont1_rate=2.00,
              cont2_g=100, cont2_rate=10.00)
    cost = form.calculate_cogs()
    assert cost == pytest.approx(3.00, 0.01)

def test_calc_labor_logic(form):
    """
    Test 5: Labor Calculation.
    30 mins @ $20/hr = 0.5hr * $20 = $10.00
    """
    setup_bom(form, labor_min=30, labor_rate=20)
    cost = form.calculate_cogs()
    assert cost == pytest.approx(10.00, 0.01)

def test_calc_empty_inputs(form):
    """
    Test 6: Empty strings should be treated as 0.
    """
    # use setup_bom to clear everything to known state (0/1), then override specific fields to ""
    # We want ALL fields to be empty strings to test safety? 
    # Or just ensure the ones we care about are empty, others are 0.
    # calculate_cogs iterates all rows.
    # If we leave others as defaults (0), they add 0.
    # If we set wax to "", get_val returns 0.
    setup_bom(form, wax_g="", wax_rate="", labor_min="")
    
    cost = form.calculate_cogs()
    assert cost == 0.0

def test_calc_invalid_inputs(form):
    """
    Test 7: Garbage text inputs should be treated as 0 (safe float conversion).
    """
    setup_bom(form, 
              wax_g="abc", wax_rate="ten", 
              labor_min="NaN")
    
    cost = form.calculate_cogs()
    assert cost == 0.0

def test_calc_zero_quantities(form):
    """
    Test 8: Valid rates but 0 quantity should result in 0 cost.
    """
    setup_bom(form, 
              wax_g=0, wax_rate=100,
              cont1_qty=0, cont1_rate=5.00)
    cost = form.calculate_cogs()
    assert cost == 0.0

def test_calc_full_complex_bom(form):
    """
    Test 9: All fields populated.
    Wax: 100g @ $10/kg = $1.00
    Frag: 10g @ $50/kg = $0.50
    Wick: 1 @ $0.10 = $0.10
    Cont1: 1 @ $1.40 = $1.40
    Cont2: 50g @ $20/kg = $1.00
    Box: 1 @ $0.50 = $0.50
    Wrap: $0.25
    Card: $0.10
    Labor: 15min @ $20/hr = $5.00
    
    Sum: 1+0.5+0.1+1.4+1+0.5+0.25+0.1+5 = 9.85
    """
    setup_bom(form,
              wax_g=100, wax_rate=10,
              frag_g=10, frag_rate=50,
              wick_qty=1, wick_rate=0.10,
              cont1_qty=1, cont1_rate=1.40,
              cont2_g=50, cont2_rate=20,
              box_qty=1, box_rate=0.50,
              wrap=0.25, biz_card=0.10,
              labor_min=15, labor_rate=20)
    
    cost = form.calculate_cogs()
    assert cost == pytest.approx(9.85, 0.01)

def test_weight_calc_summation(form):
    """
    Test 10: Auto-calculated weight should include Wax + Frag + Gypsum (Cont2).
    Wax: 100g
    Frag: 10g
    Cont1: 1 unit (Should be IGNORED for weight calc typically, as it's separate item, or at least that's current logic?)
    Cont2: 200g (Gypsum)
    
    Expected Weight: 100 + 10 + 200 = 310g
    """
    setup_bom(form,
              wax_g=100, frag_g=10,
              cont1_qty=1, # Glass, shouldn't add to "calculated weight" logic if logic only sums pourable/moldable?
              # Let's check logic: calculate_cogs adds cont2_g to weight.
              cont2_g=200)
    
    form.calculate_cogs()
    
    # Check what was inserted into entry_weight
    # MockObject.delete(0, END) -> MockObject.insert(0, "310.0")
    # We inspect the calls to insert.
    
    # Get all calls to insert on entry_weight
    calls = form.entry_weight.insert.call_args_list
    assert len(calls) > 0
    # Last call should be the update: insert(0, "310.0")
    args, _ = calls[-1]
    assert args[0] == 0
    # args[1] could be float or string
    assert float(args[1]) == 310.0

def test_calc_decimal_rounding(form):
    """
    Test 11: Very small fractional amounts.
    Wax: 1g @ $12.34/kg = $0.01234 -> $0.01 rounded?
    Wait, logic uses floats until end? 
    Display in tree is usually formatted .2f. 
    Total COGS is returned as float.
    Let's check if it sums full precision.
    """
    setup_bom(form, wax_g=1, wax_rate=12.34)
    cost = form.calculate_cogs()
    # 0.01234
    assert cost == pytest.approx(0.01234, 0.00001)

def test_calc_high_value(form):
    """
    Test 12: High value inputs (Gold flake candle?).
    Container: 1 @ $500.00
    Labor: 10 hrs @ $100/hr = $1000
    Total = $1500
    """
    setup_bom(form, cont1_qty=1, cont1_rate=500, labor_min=600, labor_rate=100)
    cost = form.calculate_cogs()
    assert cost == 1500.00

def test_calc_multiple_wicks(form):
    """
    Test 13: 3 wicks @ $0.15.
    Total: $0.45
    """
    setup_bom(form, wick_qty=3, wick_rate=0.15)
    cost = form.calculate_cogs()
    assert cost == pytest.approx(0.45, 0.01)

def test_rec_price_update(form):
    """
    Test 14: Verify Recommended Price field is updated.
    Formula: (Material * M) + Labor.
    Let's assume material cost = $5.00, Labor = $0.00.
    Config defaults: M defined by curve.
    We need to check that entry_rec_price.insert was called logic.
    """
    # Force mock return regarding recommended price
    # We can't easily check the *value* unless we calculate curve too.
    # But checking it was updated is enough for "logic runs".
    setup_bom(form, cont1_qty=1, cont1_rate=5.00)
    
    form.calculate_cogs()
    
    # Check insert called
    calls = form.entry_rec_price.insert.call_args_list
    assert len(calls) > 0
    # Last call should contain some text
    args, _ = calls[-1]
    text_inserted = args[1] 
    # Format is usually "$XX.XX (xM.MM)"
    assert "$" in text_inserted
    assert "(x" in text_inserted

def test_weight_calc_ignore_non_weight_items(form):
    """
    Test 15: Ensure Wicks, Box, Units do not add to 'Weight(g)' field.
    Only Wax, Frag, and Gypsum (Cont2) should add.
    """
    setup_bom(form, 
              wick_qty=10, 
              box_qty=5, 
              cont1_qty=5, # Glass
              wax_g=100)
    
    form.calculate_cogs()
    
    # Weight should just be 100
    calls = form.entry_weight.insert.call_args_list
    args, _ = calls[-1]
    assert float(args[1]) == 100.0

def test_calc_partial_labor(form):
    """
    Test 16: 1 minute of labor.
    1/60 * $60/hr = $1.00
    """
    setup_bom(form, labor_min=1, labor_rate=60)
    cost = form.calculate_cogs()
    assert cost == pytest.approx(1.00, 0.01)

def test_calc_negative_handler(form):
    """
    Test 17: Negative inputs should ideally be handled or ignored.
    get_val handles negatives? Logic usually:
    val = float(str) ... if val > 0.
    If code says `if cont_rate > 0`, negatives might be excluded.
    Let's check logic in product_form.py:
    `cont_rate = get_val(...)`
    `if cont_rate > 0:` -> So negative rate is ignored (Cost = 0).
    """
    setup_bom(form, cont1_qty=1, cont1_rate=-5.00)
    cost = form.calculate_cogs()
    # Should be 0 because `if rate > 0` block is skipped
    assert cost == 0.0

def test_calc_only_box(form):
    """
    Test 18: Just a box.
    """
    setup_bom(form, box_qty=10, box_rate=0.50)
    cost = form.calculate_cogs()
    assert cost == 5.00

def test_calc_only_wrap(form):
    """
    Test 19: Just wrap cost (flat fee).
    """
    setup_bom(form, wrap=1.50)
    cost = form.calculate_cogs()
    assert cost == 1.50

def test_calc_only_biz_card(form):
    """
    Test 20: Just biz card cost.
    """
    setup_bom(form, biz_card=0.05)
    cost = form.calculate_cogs()
    assert cost == 0.05

def test_full_complex_defaults(form):
    """
    Test 21: Verify that setup_bom defaults (0 cost) result in 0 total.
    """
    # No args -> all 0
    setup_bom(form) 
    cost = form.calculate_cogs()
    assert cost == 0.0
