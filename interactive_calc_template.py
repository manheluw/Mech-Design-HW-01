"""
================================================================================
INTERACTIVE VARIABLE INPUT TEMPLATE v4.0
================================================================================
Python: 3.10+ (3.14 compatible)

Features:
- Dynamic number of variables (add/remove without losing data)
- Special constants: pi, e, i, sqrt2, sqrt3, phi, inf
- Value + Name inputs for each variable
================================================================================
"""

import numpy as np

try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    JUPYTER_MODE = True
except ImportError:
    JUPYTER_MODE = False
    print("Requires Jupyter + ipywidgets. Install: pip install ipywidgets")


# Special constants that can be typed in value boxes
CONSTANTS = {
    'pi': np.pi,
    'e': np.e,
    'i': 1j,
    'j': 1j,
    'sqrt2': np.sqrt(2),
    'sqrt3': np.sqrt(3),
    'phi': (1 + np.sqrt(5)) / 2,  # Golden ratio
    'inf': np.inf,
    'nan': np.nan,
}


def parse_value(text):
    """
    Parse a value that might be a number or a constant.
    Supports: pi, e, i, j, sqrt2, sqrt3, phi, inf
    Also supports expressions like: 2*pi, pi/2, e**2
    """
    text = str(text).strip().lower()
    
    # Direct constant lookup
    if text in CONSTANTS:
        return CONSTANTS[text]
    
    # Try to evaluate as expression with constants
    try:
        # Create safe namespace with constants
        namespace = {
            'pi': np.pi,
            'e': np.e,
            'i': 1j,
            'j': 1j,
            'sqrt': np.sqrt,
            'sqrt2': np.sqrt(2),
            'sqrt3': np.sqrt(3),
            'phi': (1 + np.sqrt(5)) / 2,
            'inf': np.inf,
            'exp': np.exp,
            'log': np.log,
            'sin': np.sin,
            'cos': np.cos,
        }
        result = eval(text, {"__builtins__": {}}, namespace)
        return result
    except:
        pass
    
    # Try as plain number
    try:
        return float(text)
    except:
        pass
    
    # Return as string if nothing works
    return text


class VariableInterface:
    """
    Interactive interface with dynamic number of variable inputs.
    """
    
    def __init__(self, n_variables=3, title="Parameter Input", callback=None):
        self.n_variables = n_variables
        self.title = title
        self.callback = callback
        self.value_widgets = {}
        self.name_widgets = {}
        self.output = None
        self.var_container = None
        self.n_input = None
        
    def create_interface(self):
        if not JUPYTER_MODE:
            print("Error: Jupyter environment required")
            return self
        
        # Header
        header = widgets.HTML(f'''
        <div style="
            background: linear-gradient(135deg, #1a5276 0%, #2e86ab 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h2 style="color: white; margin: 0; text-align: center;">⚙️ {self.title}</h2>
            <p style="color: #d5e8f0; text-align: center; margin: 8px 0 0 0;">
                Supports: pi, e, i, sqrt2, sqrt3, phi, inf, expressions (2*pi, e**2)
            </p>
        </div>
        ''')
        
        # Number of variables control
        self.n_input = widgets.IntText(
            value=self.n_variables,
            layout=widgets.Layout(width='80px'),
            style={'description_width': '0px'}
        )
        
        update_btn = widgets.Button(
            description='Update Count',
            button_style='info',
            layout=widgets.Layout(width='120px', height='32px')
        )
        update_btn.on_click(self._update_variable_count)
        
        n_control = widgets.HBox([
            widgets.HTML('<div style="padding:5px 10px;font-weight:bold;color:#1a5276;"># Variables:</div>'),
            self.n_input,
            update_btn
        ], layout=widgets.Layout(margin='0 0 10px 0'))
        
        # Variable rows container
        self.var_container = widgets.VBox([])
        self._build_variable_rows()
        
        # Main container for variables
        main_container = widgets.VBox([
            n_control,
            self.var_container
        ], layout=widgets.Layout(
            padding='15px',
            border='2px solid #2e86ab',
            border_radius='10px'
        ))
        
        # Run button
        self.run_button = widgets.Button(
            description='▶ Run!',
            button_style='success',
            layout=widgets.Layout(width='200px', height='45px', margin='15px 0')
        )
        self.run_button.on_click(self._on_run)
        
        # Status
        self.status = widgets.HTML('<div style="color:#888;font-size:12px;">Ready</div>')
        
        # Output area
        self.output = widgets.Output()
        
        # Full interface
        interface = widgets.VBox([
            header,
            main_container,
            widgets.HBox([self.run_button, self.status], 
                layout=widgets.Layout(align_items='center', gap='15px')),
            self.output
        ])
        
        display(interface)
        return self
    
    def _build_variable_rows(self):
        """Build or rebuild variable input rows."""
        rows = []
        
        # Column headers
        col_header = widgets.HBox([
            widgets.HTML('<div style="width:100px;"></div>'),
            widgets.HTML('<div style="width:150px;font-weight:bold;color:#1a5276;text-align:center;">Value</div>'),
            widgets.HTML('<div style="width:200px;font-weight:bold;color:#1a5276;text-align:center;">Name</div>')
        ])
        rows.append(col_header)
        
        for i in range(1, self.n_variables + 1):
            key = f'var{i}'
            
            label = widgets.HTML(
                f'<div style="width:100px;padding:8px 0;font-weight:bold;color:#2e86ab;">Variable {i}:</div>'
            )
            
            # Preserve existing value or create new
            if key in self.value_widgets:
                old_val = self.value_widgets[key].value
            else:
                old_val = '0'
            
            value_widget = widgets.Text(
                value=str(old_val),
                placeholder='number or pi, e, i...',
                layout=widgets.Layout(width='140px'),
                style={'description_width': '0px'}
            )
            
            # Preserve existing name or create new
            if key in self.name_widgets:
                old_name = self.name_widgets[key].value
            else:
                old_name = f'var{i}'
            
            name_widget = widgets.Text(
                value=old_name,
                placeholder=f'Name for variable {i}',
                layout=widgets.Layout(width='190px'),
                style={'description_width': '0px'}
            )
            
            self.value_widgets[key] = value_widget
            self.name_widgets[key] = name_widget
            
            row = widgets.HBox([label, value_widget, name_widget],
                layout=widgets.Layout(margin='3px 0'))
            rows.append(row)
        
        # Remove old widgets beyond current count
        keys_to_remove = [k for k in self.value_widgets if int(k[3:]) > self.n_variables]
        for k in keys_to_remove:
            del self.value_widgets[k]
            del self.name_widgets[k]
        
        self.var_container.children = rows
    
    def _update_variable_count(self, button):
        """Handle update count button click."""
        new_n = self.n_input.value
        if new_n < 1:
            new_n = 1
            self.n_input.value = 1
        if new_n > 50:
            new_n = 50
            self.n_input.value = 50
        
        self.n_variables = new_n
        self._build_variable_rows()
        self.status.value = f'<div style="color:#28a745;font-size:12px;">✓ Updated to {new_n} variables</div>'
    
    def get_variables(self):
        """
        Get current values as dict.
        Returns: {'var1': {'value': x, 'name': 'custom_name'}, ...}
        """
        result = {}
        for key in self.value_widgets:
            raw_value = self.value_widgets[key].value
            parsed_value = parse_value(raw_value)
            result[key] = {
                'value': parsed_value,
                'raw': raw_value,
                'name': self.name_widgets[key].value
            }
        return result
    
    def get_values_by_name(self):
        """Returns: {'custom_name1': value1, ...}"""
        result = {}
        for key in self.value_widgets:
            name = self.name_widgets[key].value
            raw_value = self.value_widgets[key].value
            result[name] = parse_value(raw_value)
        return result
    
    def get_values_list(self):
        """Get values as list."""
        return [parse_value(self.value_widgets[f'var{i}'].value) 
                for i in range(1, self.n_variables + 1)]
    
    def get_names_list(self):
        """Get names as list."""
        return [self.name_widgets[f'var{i}'].value 
                for i in range(1, self.n_variables + 1)]
    
    def _on_run(self, button):
        self.status.value = '<div style="color:#2e86ab;font-size:12px;">⏳ Running...</div>'
        
        with self.output:
            clear_output(wait=True)
            
            if self.callback:
                try:
                    self.callback(self.get_variables())
                    self.status.value = '<div style="color:#28a745;font-size:12px;">✓ Complete</div>'
                except Exception as e:
                    self.status.value = f'<div style="color:#dc3545;font-size:12px;">✗ Error</div>'
                    import traceback
                    traceback.print_exc()
            else:
                print("="*50)
                print("VARIABLES")
                print("="*50)
                for key, data in self.get_variables().items():
                    print(f"  {data['name']} = {data['value']} (input: {data['raw']})")
                print("="*50)
                self.status.value = '<div style="color:#28a745;font-size:12px;">✓ Printed</div>'


def create_variable_interface(n_variables=3, title="Parameter Input", callback=None):
    """
    Create and display the interface.
    
    Args:
        n_variables: Initial number of variables
        title: Title at top
        callback: Function to run on button click
    
    Returns:
        VariableInterface instance
    """
    interface = VariableInterface(n_variables, title, callback)
    interface.create_interface()
    return interface


if __name__ == "__main__":
    print("Interactive Variable Input Template v4.0")
    print(f"Jupyter mode: {JUPYTER_MODE}")
    print(f"Constants available: {list(CONSTANTS.keys())}")