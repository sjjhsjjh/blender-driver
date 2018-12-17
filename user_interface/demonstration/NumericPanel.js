// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

export default class NumericPanel {
    constructor(control, text, name, move) {
        this._control = control;
        this._text = text;
        this._name = name;
        this._move = move;

        this._panel = undefined;
        this._hoverControls = [];
        
        this._inputActive = false;
        this._hoverActive = true;
    }
    
    get inputActive() {
        return this._inputActive;
    }
    set inputActive(active) {
        this._inputActive = active;
        if (this._panel === undefined) {
            return;
        }
        this._update_input_panel();
        if (active) {
            this._control.get(this._move)
            .then(got => {
                this._panel.input.value = Number.parseFloat(got).toFixed(1);
            });
        }
    }
    
    get hoverActive() {
        return this._hoverActive;
    }
    set hoverActive(active) {
        this._hoverActive = active;
        this._hoverControls.forEach(
            control => this._update_hover_control(control));
    }
    
    show(userInterface, parent) {
        const panel = userInterface.append_node('span', undefined, parent);
        panel.classList.add('panel');
        
        ["++", "+", false, "-", "--"].forEach(label => {
            if (label) {
                this._hoverControls.push(this.add_hover_control(
                    userInterface, label, panel));
            }
            else {
                this.add_input_control(userInterface, panel);
            }
        });

        return panel;
    }
    
    add_hover_control(userInterface, label, parent) {
        const control = userInterface.append_node('span', label, parent);
        control.classList.add("hoverControl");
        this._update_hover_control(control);
        const sign = label[0] == '+' ? 1 : -1;
        const moveDescription = `move ${label} "${this._text}"`;
        const stopDescription = `stop ${label} "${this._text}"`;
        const factor = label.length * label.length * sign;
        control.onmouseover = () => {
            if (this.hoverActive) {
                this._control.move(moveDescription, this._move, factor);
            }
        };
        control.onmouseout = () => {
            if (this.hoverActive) {
                this._control.stop(stopDescription, this._move);
            }
        };
        control.onclick = () => {
            this._control.activateInputControls(false);
            this._control.activateHoverControls(true);
            this._control.move(moveDescription, this._move, factor);
        };
        return control;
    }

    _update_hover_control(control) {
        if (this.hoverActive) {
            control.removeAttribute('title');
            control.classList.remove("hoverControl-inactive");
            control.classList.add("hoverControl-active");
        }
        else {
            control.setAttribute('title', "Click to activate hover controls.");
            control.classList.remove("hoverControl-active");
            control.classList.add("hoverControl-inactive");
        }
        return control;
    }
    
    add_input_control(userInterface, parent) {
        this._panel = userInterface.add_numeric_input(
            this._name, "0.0", this._text, parent);
        this._update_input_panel();

        this._panel.input.onchange = () => {
            const value = parseFloat(this._panel.input.value);
            this._control.set(value, this._move);
        };
            
        this._panel.label.onclick = () => {
            const active = this.inputActive;
            // Toggle activation of hover and input controls.
            this._control.activateInputControls(!active);
            this._control.activateHoverControls(active);
        };

        return this._panel.label;
    }
    
    _update_input_panel() {
        const panel = this._panel.panel;
        const control = this._panel.input;
        if (this.inputActive) {
            panel.removeAttribute('title');
            control.removeAttribute('title');
            control.disabled = false;
        }
        else {
            panel.setAttribute('title', "Click to activate input.");
            control.setAttribute('title', "Click above to activate input.");
            control.disabled = true;
        }
        return control;
    }
        
}