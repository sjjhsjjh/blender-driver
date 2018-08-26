// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

class UserInterface {
    create_node(tag, text) {
        var element = document.createElement(tag);
        if ( text !== undefined ) {
            element.appendChild(document.createTextNode(text));
        }
        return element;
    }
    
    append_node(tag, text, parent) {
        if (parent === undefined) {
            parent = this.userInterface;
        }
        return parent.appendChild(this.create_node(tag, text));
    }
    
    remove_childs(parent) {
        while(true) {
            const child = parent.firstChild;
            if (child === null) {
                break;
            }
            parent.removeChild(child);
        }
    }
    
    add_button(text, boundMethod, parent) {
        const button = this.append_node('button', text, parent);
        button.setAttribute('type', 'button');
        button.onclick = () => boundMethod();
        return button;
    }
    
    add_numeric_input(name, defaultValue, label, parent) {
        const panel = this.append_node('div', undefined, parent);
        const labelNode = this.append_node('label', label, panel);
        const input = this.append_node('input', undefined, panel);
        input.setAttribute('type', 'number');
        input.setAttribute('name', name);
        labelNode.setAttribute('for', name);
        if (defaultValue !== undefined) {
            input.setAttribute('value', defaultValue);
            this.formValues[name] = defaultValue;
        }
        input.onchange = () => {
            this.formValues[name] = input.value;
        };
        return input;
    }
    
    add_tickbox(name, label, parent) {
        const input = this.append_node('input', undefined, parent);
        input.setAttribute('type', 'checkbox');
        input.setAttribute('name', name);
        const labelNode = this.append_node('label', label, parent);
        labelNode.setAttribute('for', name);
        this.formValues[name] = false;
        input.onchange = () => {
            this.formValues[name] = input.checked;
        };
        return input;
    }
    
    add_camera_panel(text, dimension, unit, parent) {
        const panel = this.append_node('span', undefined, parent);
        panel.setAttribute('class', 'panel');
        
        ["++", "+", null, "-", "--"].forEach(
            label => this.add_camera_control(
                label, text, dimension, unit, panel));

        return panel;
    }
    
    add_camera_control(label, text, dimension, unit, parent) {
        if (label === null) {
            const node = this.append_node('span', text, parent);
            node.setAttribute('class', 'label');
            return node;
        }
        const control = this.append_node('span', label, parent);
        control.setAttribute('class', 'control');
        const sign = label[0] == '+' ? 1 : -1;
        control.onmouseover = () => {
            this.camera_move("mouse over " + label + ' "' + text + '"',
                             dimension,
                             unit * label.length * label.length * sign);
        };
        control.onmouseout = () => {
            this.camera_stop("mouse out " + label);
        };
        return control;
    }

    camera_move(mouseEvent, dimension, amount) {
        if (this.formValues.verboseMouseEvents) {
            this.add_text_results(mouseEvent + " " + JSON.stringify(dimension));
        }
        this.fetch(
            "PUT", {
                "valuePath": ["root", "camera", ...dimension],
                "speed": amount
            }, 'animations', 'user_interface', 'camera'
        );
    }

    camera_stop(mouseEvent) {
        if (this.formValues.verboseMouseEvents) {
            this.add_text_results(mouseEvent);
        }
        this.fetch("DELETE", 'animations', 'user_interface', 'camera');
    }
    
    add_results(...objects) {
        objects.forEach(item => 
            this.results.insertBefore(
                document.createTextNode(JSON.stringify(item, null, "  ")),
                this.results.firstChild)
        );
        this.results.normalize();
    }

    add_text_results(...texts) {
        texts.forEach(item => 
            this.results.insertBefore(
                document.createTextNode(item + "\n"),
                this.results.firstChild)
        );
        this.results.normalize();
    }
    
    clear_results() {
        this.fetches = 0;
        this.remove_childs(this.fetchCountDisplay);
        this.remove_childs(this.results);
    }

    constructor(userInterfaceID) {
        this._timeOut = undefined;
        this._stopped = false;
        this._fetches = 0;
        this.userInterface = document.getElementById(userInterfaceID);
        this.fetchCountDisplay = undefined;
        this.formValues = {};
    }
    
    get fetches() {
        return this._fetches;
    }
    set fetches(count) {
        this._fetches = count;
        const fetchCount = 'Fetches:' + this.fetches + ".";
        if (this.fetchCountDisplay === undefined) {
            console.log(fetchCount);
            return;
        }
        this.remove_childs(this.fetchCountDisplay);
        this.append_node('span', fetchCount, this.fetchCountDisplay);
    }
    
    api_path(path) {
        const prefix = 'api';
        if (path === undefined) {
            return prefix;
        }
        return [prefix, ...path].join('/');
    }
    
    go_fence() {
        const separation = parseFloat(this.formValues.separation);
        const posts = parseInt(this.formValues.posts);
        const turn = (
            (parseFloat(this.formValues.turnDegrees) / 180.0) * Math.PI);
        const height = parseFloat(this.formValues.height);
        
        const xStart = -1.5;
        const yStart = -3.5;
        const zStart = 0.5 + height;
        
        let x = xStart;
        let y = yStart;
        let z = zStart;
        let angle = 0;

        this.stopped = false;
        this.toBuild = [];
        for(var postIndex=0; postIndex<posts; postIndex++) {
            this.toBuild.push({"patch":{
                "rotation": [0, 0, angle],
                "worldPosition": [x, y, z],
                "worldScale": [1.0, 1.0, height],
                "physics": false
            }});
            this.toBuild.push({"patch":{
                "rotation": [0, 0, angle + (0.25 * Math.PI)],
                "worldPosition": [x, y, z + height + 2.0],
                "worldScale": [1.0, 1.0, 0.5],
                "physics": false
            }});
            x += separation * Math.cos(angle);
            y += separation * Math.sin(angle);
            angle += turn;
        }
        this.reset().then(() => this.build_one_fence(0, this.toBuild.length));
    }
    
    build_one_fence(index, count) {
        this._timeOut = undefined;
        if (this.stopped) {
            this.add_text_results("Stopped.");
            return;
        }

        const patch = this.toBuild[index].patch;
        const scale = patch.worldScale;
        delete patch.worldScale;
        this.fetch("PATCH", patch, 'root', 'gameObjects', index)
        .then((response) =>
            (this.formValues.trackBuild || index == 0) ?
            this.fetch("PUT", ['root', 'gameObjects', index],
                       'root', 'cursors', 0, 'subjectPath') :
            Promise.resolve(response))
        .then(() =>
            this.fetch("PATCH", scale[2],
                       'root', 'gameObjects', index, 'worldScale', 2))
        .then((response) =>
            (index % 2 == 1) ?
            this.fetch("PUT", {
                    "modulo": 2.0 * Math.PI,
                    "speed": (2.0 / 3.0) * Math.PI,
                    "valuePath": ["root", 'gameObjects', index, 'rotation', 2]
                }, 'animations', 'gameObjects', Math.trunc(index / 2)) :
            Promise.resolve(response))
        .then(() => {
            index++;
            if (index >= count) {
                const floorMargin = 1.0;
                const dimensions = this.toBuild.reduce(
                  (accumulator, item) => {
                    const values = item.patch.worldPosition;
                    if (accumulator.xMin === undefined ||
                        values[0] < accumulator.xMin
                    ) {
                        accumulator.xMin = values[0];
                    }
                    if (accumulator.yMin === undefined ||
                        values[1] < accumulator.yMin
                    ) {
                        accumulator.yMin = values[1];
                    }
                    if (accumulator.xMax === undefined ||
                        values[0] > accumulator.xMax
                    ) {
                        accumulator.xMax = values[0];
                    }
                    if (accumulator.yMax === undefined ||
                        values[1] > accumulator.yMax
                    ) {
                        accumulator.yMax = values[1];
                    }
                    return accumulator;
                  }, {
                    "xMin": undefined,
                    "yMin": undefined,
                    "xMax": undefined,
                    "yMax": undefined
                  }
                );
                let setFloor = (dimensions.xMin !== undefined &&
                                dimensions.xMax !== undefined &&
                                dimensions.yMin !== undefined &&
                                dimensions.yMax !== undefined);
                if (setFloor) {
                    dimensions.xMin -= floorMargin;
                    dimensions.yMin -= floorMargin;
                    dimensions.xMax += floorMargin;
                    dimensions.yMax += floorMargin;
                }
                console.log('accumulator', dimensions, setFloor);
                (
                    (!this.formValues.trackBuild) ?
                    this.fetch("PUT",
                               ['root', 'gameObjects', Math.trunc(index/2)],
                               'root', 'cursors', 0, 'subjectPath') :
                    Promise.resolve(null)
                )
                .then(() =>
                    setFloor ?
                        this.fetch(
                            "PUT", (
                                dimensions.xMax - dimensions.xMin
                            ), 'root', 'floor', 'worldScale', 0
                            ).then(() =>
                        this.fetch(
                            "PUT", (
                                dimensions.yMax - dimensions.yMin
                            ), 'root', 'floor', 'worldScale', 1)
                            ).then(() =>
                        this.fetch(
                            "PUT", (
                                0.5 * (dimensions.xMax + dimensions.xMin)
                            ), 'root', 'floor', 'worldPosition', 0)
                            ).then(() =>
                        this.fetch(
                            "PUT", (
                                0.5 * (dimensions.yMax + dimensions.yMin)
                            ), 'root', 'floor', 'worldPosition', 1)
                        ) :
                    Promise.resolve(null))
                .then(() => this.get_display());
            }
            else {
                this._timeOut = setTimeout(
                    this.build_one_fence.bind(this), 1, index, count);
            }
        });
    }
    
    tower() {
        const xCount = 4;
        const yCount = 4;
        const zCount = 4;
        const increment = 2.5;
        const xStart = -1.5;
        const yStart = -3.5;
        const zStart = 0.5;
        
        let objectIndex = 0;
        let x = xStart;
        let y = yStart;
        let z = zStart;
        let objectCount;
        
        let xIndex = 0;
        let yIndex = 0;
        let zIndex = 0;

        this.stopped = false;

        // Following code is based on a time out, but used to be based on an
        // interval. The interval seems more conceptually correct, but the time
        // out ensures that the above variables get incremented in
        // synchronisation with the PATCH requests. If they get out of
        // synchronisation, then an objectIndex can be duplicated and skipped,
        // like 8 goes twice and 9 is skipped.
        let phase = 2;
        function add_one(that) {
            that._timeOut = undefined;
            if (that.stopped) {
                that.add_text_results("Stopped.");
                return;
            }
            const patch = (phase === 2) ?
                {
                    "rotation": [0, 0, 0],
                    "worldPosition": [x, y, z],
                    "physics": false
                } : {
                    "physics": true
                };
            that.fetch("PATCH", patch, 'root', 'gameObjects', objectIndex)
            .then(() => {
                objectIndex += 1;
                
                if (phase === 2) {
                    zIndex += 1;
                    z += increment;
                    if (zIndex >= zCount) {
                        zIndex = 0;
                        z = zStart;
        
                        yIndex += 1;
                        y += increment;
                        if (yIndex >= yCount) {
                            yIndex = 0;
                            y = yStart;
        
                            xIndex += 1;
                            x += increment;
                            if (xIndex >= xCount) {
                                phase -= 1;
                                objectCount = objectIndex;
                                objectIndex = 0;
                            }
                        }
                    }
                }
                else if (phase == 1) {
                    if (objectIndex >= objectCount) {
                        phase -= 1;
                        objectIndex = 0;
                    }
                }
                
                if (phase <= 0) {
                    that.get_display();
                }
                else {
                    that._timeOut = setTimeout(
                        add_one, (phase === 2 ? 10 : 1), that);
                }
            });
        }
        this.reset().then(() => add_one(this));
    }
    
    reset() {
        if (this._timeOut !== undefined) {
            clearTimeout(this._timeOut);
            this._timeOut = undefined;
        }
        return this.fetch("DELETE", 'animations', 'gameObjects')
        .then(() => this.fetch("DELETE", 'root', 'gameObjects'));
    }
    
    stop() {
        this.stopped = true;
        let message = "Deleting";
        if (this._timeOut !== undefined) {
            message += " and clearing time out:" + this._timeOut;
        }
        message += ".";
        this.reset().then(() => this.add_text_results(message));
    }
    
    fetch(method, ...parameters) {
        this.fetches++;
        const options = {"method": method};
        if (method !== "DELETE") {
            options.body = JSON.stringify(parameters.shift());
        }
        return fetch(this.api_path(parameters), options)
        .then(response => response.text());
    }
    
    get_display() {
        this.fetches++;
        return fetch(this.api_path())
        .then(response => response.json())
        .then(response => {
            this.add_results(response);
            return Promise.resolve(response);
        });
    }
    
    show() {
        this.add_button("Build", this.tower.bind(this));
        this.add_button("Stop", this.stop.bind(this));
        
        const build = this.append_node('fieldset');
        
        this.append_node('legend', "Fence", build);
        this.add_numeric_input('posts', 10, 'Posts:', build);
        this.add_numeric_input('separation', 4.0, 'Separation:', build);
        this.add_numeric_input(
            'turnDegrees', 5.0, 'Deviation (degrees):', build);
        this.add_numeric_input('height', 3.0, 'Height:', build);
        this.add_button("Build", this.go_fence.bind(this), build);

        const camera = this.append_node('fieldset');
        camera.setAttribute('id', 'camera');
        this.append_node('legend', "Camera", camera);
        this.add_camera_panel("Zoom", ["orbitDistance"], -5.0, camera);
        this.add_camera_panel("Orbit", ["orbitAngle"], -0.5, camera);
        this.add_camera_panel("Altitude", ["worldPosition", 2], 5.0, camera);
        this.add_camera_panel("X", ["worldPosition", 0], 5.0, camera);
        this.add_camera_panel("Y", ["worldPosition", 1], 5.0, camera);
        this.add_tickbox('trackBuild', "Track build", camera);

        const results = this.append_node('fieldset');
        this.append_node('legend', "Results", results);
        this.add_button("Clear", this.clear_results.bind(this), results);
        this.add_button("Fetch /", this.get_display.bind(this), results);
        this.add_tickbox('verboseMouseEvents', "Verbose mouse events", results);
        this.fetchCountDisplay = this.append_node('div', undefined, results);
        this.results = this.append_node('pre', undefined, results);
        
        return this;
    }
}

function main(userInterfaceID) {
    const userInterface = new UserInterface(userInterfaceID);
    return userInterface.show();
}