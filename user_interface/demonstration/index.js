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
    
    add_numeric_input(name, defaultString, label, parent) {
        // The default value must be passed as a string to distinguish 4 from
        // 4.0 for example.
        const panel = this.append_node('div', undefined, parent);
        const labelNode = this.append_node('label', label, panel);
        const input = this.append_node('input', undefined, panel);
        input.setAttribute('type', 'number');
        input.setAttribute('name', name);
        labelNode.setAttribute('for', name);
        const isFloat = (defaultString !== undefined &&
                         defaultString.includes("."));
        const parseValue = (isFloat ? parseFloat : parseInt);
        if (defaultString !== undefined) {
            input.setAttribute('value', parseValue(defaultString));
            this.formValues[name] = parseValue(defaultString);
            input.setAttribute('step', isFloat ? 0.1 : 1);
        }
        input.onchange = () => {
            this.formValues[name] = parseValue(input.value);
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
    
    go_fence() {
        const separation = this.formValues.fenceSeparation;
        const posts = this.formValues.posts;
        const turn = (this.formValues.turnDegrees / 180.0) * Math.PI;
        const height = this.formValues.height;
        
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
            //
            // Fence post.
            this.toBuild.push({"cube":{
                "rotation": [0, 0, angle],
                "worldPosition": [x, y, z],
                "worldScale": [1.0, 1.0, height]
            }});
            //
            // Fence cap.
            this.toBuild.push({
                "cube":{
                    "rotation": [0, 0, angle + (0.25 * Math.PI)],
                    "worldPosition": [x, y, z + height + 2.0],
                    "worldScale": [1.0, 1.0, 0.5],
                    "physics": false
                },
                "animation":{
                    "specification":{
                        "modulo": 2.0 * Math.PI,
                        "speed": (2.0 / 3.0) * Math.PI,
                        "valuePath": ["root", 'gameObjects',
                                      (postIndex * 2) + 1 , 'rotation', 2]
                    },
                    "path": ['animations', 'gameObjects', postIndex]
                }
            });

            x += separation * Math.cos(angle);
            y += separation * Math.sin(angle);
            angle += turn;
        }
        this.build_start();
    }
    
    build_start() {
        const count = this.toBuild.length;
        return this.fetch("DELETE", 'animations', 'gameObjects')
        .then(() => this.drop())
        .then((oldCount) => this.build_one(0, oldCount, count));
    }
    
    build_one(index, oldCount, count) {
        this._timeOut = undefined;
        if (this.stopped) {
            this.add_text_results("Stopped.");
            return;
        }

        const cube = this.toBuild[index].cube;
        const scale = cube.worldScale === undefined ? [1.0, 1.0, 1.0] : cube.worldScale;
        delete cube.worldScale;
        cube.physics = false;
        const animation = this.toBuild[index].animation;
        return (
            (index < oldCount) ?
            this.fetch("PUT", null, 'root', 'gameObjects', index) :
            Promise.resolve(null)
        )
        //.then(() =>
        //    this.fetch("PUT", false, 'root', 'gameObjects', index, 'physics'))
        .then(() =>
            this.fetch("PATCH", cube, 'root', 'gameObjects', index))
        .then(() =>
            this.fetch("PUT", scale[0],
                       'root', 'gameObjects', index, 'worldScale', 0))
        .then(() =>
            this.fetch("PUT", scale[1],
                       'root', 'gameObjects', index, 'worldScale', 1))
        .then(() =>
            this.fetch("PUT", scale[2],
                       'root', 'gameObjects', index, 'worldScale', 2))
        .then((response) =>
            (this.formValues.trackBuild || index == 0) ?
            this.fetch("PUT", ['root', 'gameObjects', index],
                       'root', 'cursors', 0, 'subjectPath') :
            Promise.resolve(response))
        .then((response) =>
            (animation === undefined) ?
            Promise.resolve(response) :
            this.fetch("PUT", animation.specification, ...animation.path))
        .then((response) => {
            index++;
            if (index >= count) {
                this.build_finish(index, oldCount);
            }
            else {
                this._timeOut = setTimeout(
                    this.build_one.bind(this), 1, index, oldCount, count);
            }
            return Promise.resolve(response);
        });
    }
    
    build_finish(built, oldCount) {
        const floorMargin = 1.0;
        const dimensions = this.toBuild.reduce(
            (accumulator, item) => {
                const values = item.cube.worldPosition;
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
            });
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
        return (
            (!this.formValues.trackBuild) ?
            this.fetch("PUT",
                       ['root', 'gameObjects', Math.trunc(built/2)],
                       'root', 'cursors', 0, 'subjectPath') :
            Promise.resolve(null)
        )
        .then(() =>
            setFloor ?
            this.fetch(
                "PUT", dimensions.xMax - dimensions.xMin,
                'root', 'floor', 'worldScale', 0
            ).then(() => this.fetch(
                "PUT", dimensions.yMax - dimensions.yMin,
                'root', 'floor', 'worldScale', 1
            )).then(() => this.fetch(
                "PUT", 0.5 * (dimensions.xMax + dimensions.xMin),
                'root', 'floor', 'worldPosition', 0
            )).then(() => this.fetch(
                "PUT", 0.5 * (dimensions.yMax + dimensions.yMin),
                'root', 'floor', 'worldPosition', 1
            )) :
            Promise.resolve(null))
        .then(() => {
            const delete_one = (remaining) => {
                if (remaining > 0) {
                    return this.fetch("DELETE", 'root', 'gameObjects', built)
                    .then(() => delete_one(remaining - 1));
                }
                else {
                    return Promise.resolve(remaining);
                }
            };
            return delete_one(oldCount - built);
        })
        .then(() => this.get_add_results());
    }
    
    pile() {
        const xCount = this.formValues.depth;
        const yCount = this.formValues.width;
        const zCount = this.formValues.pileHeight;
        const separation = this.formValues.pileSeparation;

        const xStart = -1.5;
        const yStart = -3.5;
        const zStart = 0.5;
        
        this.stopped = false;
        this.toBuild = [];
        let x = xStart;
        for (var xIndex=0; xIndex<xCount; xIndex++) {
            let y = yStart;
            for (var yIndex=0; yIndex<yCount; yIndex++) {
                let z = zStart;
                for (var zIndex=0; zIndex<zCount; zIndex++) {
                    this.toBuild.push({"cube":{
                        "rotation": [0, 0, 0],
                        "worldPosition": [x, y, z]
                    }});
                    z += separation;
                }
                y += separation;
            }
            x += separation;
        }
        this.build_start();
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
    
    drop() {
        return this.get('root', 'gameObjects')
        .then(gameObjects => Promise.resolve(gameObjects.length))
        .catch(error => {
            console.log('drop caught', error);
            return Promise.resolve(0);
        })
        .then(count => {
            const drop_one = (index, count) => {
                if (index < count) {
                    return this.fetch("PUT", true,
                                      'root', 'gameObjects', index, 'physics')
                    .then(() => drop_one(index + 1, count));
                }
                else {
                    return Promise.resolve(count);
                }
            };
            return drop_one(0, count);

            //
            //const drops = [];
            //for(let index=0; index < count; index++) {
            //    drops.push(this.fetch(
            //        "PUT", true, 'root', 'gameObjects', index, 'physics'));
            //}
            //return Promise.all(drops);
        });
        //.then(dropResults => Promise.resolve(dropResults.length));
    }
    
    reset_camera() {
        const speed = 15.0;
        return this.fetch(
            "DELETE", 'animations', 'user_interface', 'camera')
        .then(() => this.fetch(
            "PUT", ['root', 'floor'], 'root', 'cursors', 0, 'subjectPath'))
        .then(() => this.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 0],
                "targetValue": 20.0
            }, 'animations', 'camera_setup', 0))
        .then(() => this.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 1],
                "targetValue": 1.0
            }, 'animations', 'camera_setup', 1))
        .then(() => this.fetch(
            "PUT", {
                "speed": speed,
                "valuePath": ["root", "camera", 'worldPosition', 2],
                "targetValue": 7.0
            }, 'animations', 'camera_setup', 2))
        ;
    }
    
    api_path(path) {
        const prefix = 'api';
        if (path === undefined) {
            return prefix;
        }
        return [prefix, ...path].join('/');
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
    
    get(...path) {
        this.fetches++;
        return fetch(this.api_path(path))
        .then(response => response.json())
        .catch(reason => Promise.reject(reason));
    }

    get_add_results(...path) {
        this.get(...path).then(response => {
            this.add_results(response);
            return Promise.resolve(response);
        });
    }
    
    show() {
        const cubes = this.append_node('fieldset');
        this.append_node('legend', "Cubes", cubes);
        const cubesButtons = this.append_node('div', undefined, cubes);
        this.add_button("Drop", this.drop.bind(this), cubesButtons);
        this.add_button("Stop", this.stop.bind(this), cubesButtons);

        const pile = this.append_node('fieldset', undefined, cubes);
        this.append_node('legend', "Pile", pile);
        this.add_numeric_input('width', "4", 'Width:', pile);
        this.add_numeric_input('depth', "3", 'Depth:', pile);
        this.add_numeric_input('pileHeight', "5", 'Height:', pile);
        this.add_numeric_input('pileSeparation', "1.5", 'Separation:', pile);
        this.add_button("Build", this.pile.bind(this), pile);

        const fence = this.append_node('fieldset', undefined, cubes);
        this.append_node('legend', "Fence", fence);
        this.add_numeric_input('posts', "10", 'Posts:', fence);
        this.add_numeric_input('fenceSeparation', "4.0", 'Separation:', fence);
        this.add_numeric_input(
            'turnDegrees', "5.0", 'Deviation (degrees):', fence);
        this.add_numeric_input('height', "3.0", 'Height:', fence);
        this.add_button("Build", this.go_fence.bind(this), fence);

        const camera = this.append_node('fieldset');
        camera.setAttribute('id', 'camera');
        this.add_button("Reset", this.reset_camera.bind(this), camera);
        this.append_node('legend', "Camera", camera);
        this.add_camera_panel("Zoom", ["orbitDistance"], -5.0, camera);
        this.add_camera_panel("Orbit", ["orbitAngle"], 0.5, camera);
        this.add_camera_panel("Altitude", ["worldPosition", 2], 5.0, camera);
        this.add_camera_panel("X", ["worldPosition", 0], 5.0, camera);
        this.add_camera_panel("Y", ["worldPosition", 1], 5.0, camera);
        this.add_tickbox('trackBuild', "Track build", camera);

        const results = this.append_node('fieldset');
        this.append_node('legend', "Results", results);
        this.add_button("Clear", this.clear_results.bind(this), results);
        this.add_button("Fetch /", this.get_add_results.bind(this), results);
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