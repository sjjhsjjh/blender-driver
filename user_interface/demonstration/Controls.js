// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

export default class Controls {
    constructor(userInterface) {
        this._userInterface = userInterface;
        this._panels = [];
    }
    
    get userInterface() {
        return this._userInterface;
    }
    
    show(parent) {
        this._panels.forEach(panel => panel.show(this.userInterface, parent));
    }

    stop(description, move) {
        if (this.userInterface.formValues.monitorMouse) {
            this.userInterface.monitor_add(description);
        }
        return this.userInterface.fetch("DELETE", ...move.animationPath);
    }

    move(description, move, factor) {
        if (this.userInterface.formValues.monitorMouse) {
            this.userInterface.monitor_add(description + " " +
                                           JSON.stringify(move.path));
        }
        return this.userInterface.fetch( "PUT", {
                "valuePath": move.path,
                "speed": move.unit * factor,
            }, ...move.animationPath);
    }

    get(move) {
        return this.userInterface.get(...move.path);
    }
    
    set(value, move) {
        return this.userInterface.fetch( "PUT", {
                "valuePath": move.path,
                "speed": move.unit * 16.0,
                "targetValue": value,
            }, ...move.animationPath);
    }

    activateInputControls(active) {
        this._panels.forEach(panel => panel.inputActive = active);
    }

    activateHoverControls(active) {
        this._panels.forEach(panel => panel.hoverActive = active);
    }
}
