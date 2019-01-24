// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import NumericPanel from './NumericPanel.js';
import Controls from './Controls.js';

export default class CursorControls extends Controls {
    constructor(userInterface) {
        super(userInterface);

        this._prefix = ['root', 'cursors', 0];
        this._animationPath = ['animations', 'user_interface', 'cursor'];
        this._axisAnimation = ['animations', 'axis', 0];
        
        this._add_panel("aX", ["axis", "x"], 1.0);
        this._add_panel("aY", ["axis", "y"], 1.0);
        this._add_panel("aZ", ["axis", "z"], 1.0);
 
        this._add_panel("X", ["origin", 0], 1.0);
        this._add_panel("Y", ["origin", 1], 1.0);
        this._add_panel("Z", ["origin", 2], 1.0);
 
        this._add_panel("Offset", ["offset"], 1.0);
        this._add_panel("Length", ["length"], 1.0);
        this._add_panel("Radius", ["radius"], 1.0);
        this._add_panel("Rotation", ["rotation"], 0.5);
    }

    show(parent) {
        const ui = this.userInterface;
        const panel = ui.append_node('div', undefined, parent);
        ui.add_button("0", this._do_move.bind(this), panel, 0);
        ui.add_button("1", this._do_move.bind(this), panel, 1);
        ui.add_button("?", this._get_face.bind(this), panel);
        //const holder = ui.add_numeric_input(null, "", null, panel);
        //holder.input.onchange = () => {
        //    this._do_move(holder.get_value() % 4);
        //};
        ui.add_button("2", this._do_move.bind(this), panel, 2);
        ui.add_button("3", this._do_move.bind(this), panel, 3);
        
        super.show(parent);
    }
    
    _get_face() {
        return this.userInterface.get(...this._prefix, 'facesOK')
        .then(ok => {
            this.userInterface.monitor_add("Faces OK 0 " + ok);
            return this.userInterface.get(...this._prefix, 'moves');
        })
        .then(moves => {
            this.userInterface.monitor_add('test get 0', moves, 'test get 1');
            return this.userInterface.get(...this._prefix, 'normal');
        })
        .then(normal =>
              this.userInterface.monitor_add(`Normal [${normal.join(",")}]`));
    }
    
    _do_move(moveIndex) {
        return this._get_face()
        .then(() => this.userInterface.get(...this._prefix, 'moves', moveIndex))
        .then(move => {
            this.userInterface.monitor_add(move, "\n");
            return this.userInterface.fetch(
                "PUT", move.preparation.value, ...move.preparation.path)
            .then(() => {
                move.animation.speed = 3.0;
                this.userInterface.fetch(
                    "PUT", move.animation, ...this._axisAnimation);
            });
        });
    }

    _add_panel(text, dimension, unit) {
        const path = [...this._prefix, ...dimension];
        this._panels.push(new NumericPanel(
            this, text, path.join('_'), {
                "path":path,
                "unit":unit,
                "subjectPath": this._prefix,
                "animationPath":this._animationPath
            }));
    }
    
}