// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import CameraControls from './CameraControls.js';
import CursorControls from './CursorControls.js';

export default class UserInterface {
    constructor(userInterfaceID) {
        this._stopped = false;
        this.userInterface = document.getElementById(userInterfaceID);
        this.clear_fetch_counts();
        this.formValues = {};
        this._progress = "";
        
        this._cameraControls = new CameraControls(this);
        this._cursorControls = new CursorControls(this);
    }
    
    clear_fetch_counts() {
        this.fetchCounts = {};
        UserInterface.methodList.forEach(
            method => this.fetchCounts[method.toLowerCase()] = 0);
        if (this.fetchCountTextNode !== undefined) {
            this.fetchCountTextNode.nodeValue = "";
        }
    }
    
    add_fetch_count(method, increment=1) {
        this.fetchCounts[method.toLowerCase()] += increment;
        if (this.fetchCountTextNode !== undefined) {
            this.fetchCountTextNode.nodeValue = [
                "HTTP", ...UserInterface.methodList.map(method =>
                    `${method}:${this.fetchCounts[method.toLowerCase()]}`
                )].join(" ");
        }
    }
    
    create_node(tag, text) {
        const textNode = (
            text === undefined ?
            undefined :
            document.createTextNode(text)
        );
        if (tag === undefined) {
            return textNode;
        }

        const element = document.createElement(tag);
        if (textNode !== undefined) {
            element.appendChild(textNode);
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
    
    add_fieldset(label, parent) {
        const fieldset = this.append_node('fieldset', undefined, parent);
        fieldset.setAttribute('id', label.toLowerCase());
        this.append_node('legend', label, fieldset);
        return fieldset;
    }
    
    add_button(text, boundMethod, parent, ...methodParameters) {
        const button = this.append_node('button', text, parent);
        button.setAttribute('type', 'button');
        button.onclick = () => boundMethod(...methodParameters);
        return button;
    }
    
    add_numeric_input(name, defaultString, label, parent) {
        // The default value must be passed as a string to distinguish 4 from
        // 4.0 for example.
        const panel = (label === null ? null :
                       this.append_node('div', undefined, parent));
        const labelNode = (label === null ? null :
                           this.append_node('label', label, panel));
        const input = this.append_node(
            'input', undefined, panel === null ? parent : panel);
        input.setAttribute('type', 'number');
        const isFloat = (defaultString !== undefined &&
                         defaultString.includes("."));
        const parseValue = (isFloat ? parseFloat : parseInt);
        if (defaultString !== undefined) {
            input.setAttribute('value', parseValue(defaultString));
            if (name !== null) {
                this.formValues[name] = parseValue(defaultString);
            }
            input.setAttribute('step', isFloat ? 0.1 : 1);
        }
        const get_value = () => parseValue(input.value);
        if (name !== null) {
            input.setAttribute('name', name);
            if (labelNode !== null) {
                labelNode.setAttribute('for', name);
            }
            input.onchange = () => {
                this.formValues[name] = get_value(); //parseValue(input.value);
            };
        }
        return {
            "panel":panel,
            "label":labelNode,
            "input":input,
            "get_value":get_value
        };
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
    
    add_cursor_panel(parent) {
        const panel = this.append_node('div', undefined, parent);
        this.add_button("<", this.move_cursor.bind(this), panel, -1);
        const input = this.append_node('input', undefined, panel);
        input.setAttribute('type', 'text');
        input.onchange = () => {
            this.move_cursor(undefined, parseInt(input.value));
        };
        this.add_button(">", this.move_cursor.bind(this), panel, 1);

        this._cursorControls.show(parent);

        return input;
    }
    
    move_cursor(increment, value, objectCount) {
        return (
            objectCount === undefined ?
            this.get('root', 'gameObjects')
            .then(gameObjects => gameObjects.length)
            .catch(() => 0) :
            Promise.resolve(objectCount)
        )
        .then(count => (
            increment === undefined ?
            Promise.resolve([count, undefined]) :
            this.get(...UserInterface.cursorSubjectPath)
            .then(path => {
                let current = path[path.length - 1];
                if (current === 'floor') {
                    current = count;
                }
                return [count, current];
            })
        ))
        .then(([count, current]) => {
            count += 1;

            // TOTH for JS modulo and negative numbers:
            // https://stackoverflow.com/a/17323608/7657675
            const nextIndex = (((
                increment === undefined ? value : current + increment
                ) % count) + count) % count;
            return this.put_cursor_subject(
                nextIndex === count - 1 ?
                ['root', 'floor'] :
                ['root', 'gameObjects', nextIndex]
            );
        });
    }
    
    get_cursor_subject() {
        return this.get(...UserInterface.cursorSubjectPath)
        .then(subject => this.display_cursor_subject(subject));
    }
    
    put_cursor_subject(subject) {
        this.display_cursor_subject(subject);
        return this.fetch("PUT", subject, ...UserInterface.cursorSubjectPath);
    }

    display_cursor_subject(subject) {
        if (this.cursorInput !== undefined) {
            // Text input elements must always receive a string value.
            // TOTH:
            // https://stackoverflow.com/questions/7609130/set-the-value-of-an-input-field#comment34884943_13826178
            this.cursorInput.value = `${subject[subject.length - 1]}`;
        }
    }

    monitor_add(...items) {
        items.forEach(item => 
            this.monitor.insertBefore(document.createTextNode(
                typeof(item) === typeof("") ?
                item + "\n" :
                JSON.stringify(item, null, "  ")
                ), this.monitor.firstChild)
        );
        this.monitor.normalize();
    }
    
    monitor_clear() {
        this.clear_fetch_counts();
        this.progress = "";
        this.remove_childs(this.monitor);
    }

    fence() {
        const separation = this.formValues.fenceSeparation;
        const posts = this.formValues.posts;
        const turn = (this.formValues.turnDegrees / 180.0) * Math.PI;
        const spin = (this.formValues.spinDegrees / 180.0) * Math.PI;
        const height = this.formValues.height;
        
        const xStart = -1.5;
        const yStart = -3.5;
        const zStart = 0.5 + height;
        
        let x = xStart;
        let y = yStart;
        let z = zStart;
        let angle = 0;

        this.stopped = false;
        const toBuild = [];
        for(var postIndex=0; postIndex<posts; postIndex++) {
            //
            // Fence post.
            toBuild.push({"cube":{
                "rotation": [0, 0, angle],
                "worldPosition": [x, y, z],
                "worldScale": [1.0, 1.0, height]
            }});
            //
            // Fence cap.
            toBuild.push({
                "cube":{
                    "rotation": [0, 0, angle + (0.25 * Math.PI)],
                    "worldPosition": [x, y, z + height + 2.0],
                    "worldScale": [1.0, 1.0, 0.5],
                    "physics": false
                },
                "animation":{
                    "specification":{
                        "modulo": 2.0 * Math.PI,
                        "speed": spin,
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
        this.build_start(toBuild);
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
        const toBuild = [];
        let x = xStart;
        for (var xIndex=0; xIndex<xCount; xIndex++) {
            let y = yStart;
            for (var yIndex=0; yIndex<yCount; yIndex++) {
                let z = zStart;
                for (var zIndex=0; zIndex<zCount; zIndex++) {
                    toBuild.push({"cube":{
                        "rotation": [0, 0, 0],
                        "worldScale": [1, 1, 1],
                        "worldPosition": [x, y, z]
                    }});
                    z += separation;
                }
                y += separation;
            }
            x += separation;
        }
        this.build_start(toBuild);
    }
    
    get progress() {
        return this._progress;
    }
    set progress(progress) {
        this.progressTextNode.nodeValue = progress;
        this._progress = progress;
    }
    
    build_start(toBuild) {
        this.progress = `To build: ${toBuild.length}.`;
        toBuild.forEach(item => Object.assign(item.cube, {"physics": false}));

        return this.fetch("DELETE", 'animations', 'gameObjects')
        .then(() => this.drop())
        .then(oldCount => (
            this.formValues.trackBuild ?
            this.build_one(0, oldCount, toBuild) :
            this.build_all(oldCount, toBuild)
        ))
        .then(([built, oldCount, toBuild]) =>
            this.build_finish(built, oldCount, toBuild)
        );
    }
    
    build_all(oldCount, toBuild) {
        // The animation.path isn't used here.
        return this.fetch(
            "PATCH", toBuild.map(item => item.cube), 'root', 'gameObjects')
        .then(() => this.fetch(
            "PATCH",
            toBuild
                .filter(item => item.animation)
                .map(item => item.animation.specification),
            'animations', 'gameObjects'))
        .then(() => Promise.resolve([toBuild.length, oldCount, toBuild]));
    }
    
    build_one(index, oldCount, toBuild) {
        const count = toBuild.length;
        const progress = ` ${index + 1} of ${count}.`;
        if (this.stopped) {
            this.progress = "Stopped at" + progress;
            return Promise.resolve([undefined, undefined, undefined]);
        }

        const cube = toBuild[index].cube;
        const animation = toBuild[index].animation;
        this.progress = "Building" + progress;
        return this.fetch("PATCH", cube, 'root', 'gameObjects', index)
        .then(() => 
            this.put_cursor_subject(['root', 'gameObjects', index]))
        .then(() =>
            (animation === undefined) ?
            Promise.resolve() :
            this.fetch("PUT", animation.specification, ...animation.path))
        .then(() =>
            index + 1 >= count ?
            Promise.resolve([index + 1, oldCount, toBuild]) :
            this.build_one(index + 1, oldCount, toBuild));
    }
    
    build_finish(built, oldCount, toBuild) {
        if (built === undefined) {
            return;
        }
        this.progress = `Built ${built}.`;
        const floorMargin = 1.0;
        const dimensions = toBuild.reduce(
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
        return (
            setFloor ?
            this.fetch("PATCH", {
                "worldScale": [dimensions.xMax - dimensions.xMin,
                               dimensions.yMax - dimensions.yMin],
                "worldPosition": [0.5 * (dimensions.xMax + dimensions.xMin),
                                  0.5 * (dimensions.yMax + dimensions.yMin)]
            }, 'root', 'floor') :
            Promise.resolve()
        )
        // If the cursor subject is about to be deleted as a surplus, move the
        // cursor to the last object.
        .then(() => this.get(...UserInterface.cursorSubjectPath))
        .then(path => {
            const current = path[path.length - 1];
            if (current === 'floor' || parseInt(current) < built) {
                return Promise.resolve();
            }
            return this.move_cursor(undefined, built - 1);
        })
        .then(() => (
            oldCount > built ?
            // On the next line, note the colon in the last path leg, which is
            // range notation.
            this.fetch("DELETE", 'root', 'gameObjects', `${built}:`)
            .then(() => Promise.resolve(oldCount - built)) :
            Promise.resolve(oldCount - built)
        ));
    }
    
    stop_spinning() {
        return this.fetch("DELETE", 'animations', 'gameObjects');
    }
    
    stop_build() {
        this.stopped = true;
    }
    
    clear() {
        this.stop_build();
        this.progress = "";
        return this.stop_spinning()
        .then(() => this.fetch(
            "PATCH", {
                'worldScale': [10.0, 10.0],
                'worldPosition': [0.0, 0.0]
            }, 'root', 'floor'))
        .then(() => this.put_cursor_subject(['root', 'floor']))
        .then(() => this.fetch("DELETE", 'root', 'gameObjects', ':'));
    }
    
    drop() {
        return this.get('root', 'gameObjects')
        .then(gameObjects => gameObjects.length)
        .catch(error => {
            console.log('drop() caught', error);
            return 0;
        })
        .then(count => {
            if (count <= 0) {
                return 0;
            }
            // Colon in quotes on the next line will create a slice of each item
            // in the gameObjects array.
            return this.fetch(
                "PUT", true, 'root', 'gameObjects', ':', 'physics')
            .then(() => count);
        });
    }
    
    api_path(path) {
        const prefix = 'api';
        if (path === undefined) {
            return prefix;
        }
        return [prefix, ...path].join('/');
    }
    
    fetch(method, ...parameters) {
        this.add_fetch_count(method);
        const options = {"method": method};
        if (method !== "DELETE") {
            options.body = JSON.stringify(parameters.shift());
        }
        return fetch(this.api_path(parameters), options)
        .then(response => response.text());
    }
    
    get(...path) {
        this.add_fetch_count("get");
        return fetch(this.api_path(path))
        .then(response => response.json())
        .catch(reason => Promise.reject(reason));
    }

    get_monitor(...path) {
        this.get(...path).then(response => {
            this.monitor_add(response);
            return Promise.resolve(response);
        });
    }
    
    show() {
        const construct = this.add_fieldset("Construct");

        const pile = this.add_fieldset("Pile", construct);
        this.add_numeric_input('width', "2", 'Width:', pile);
        this.add_numeric_input('depth', "1", 'Depth:', pile);
        this.add_numeric_input('pileHeight', "3", 'Height:', pile);
        this.add_numeric_input('pileSeparation', "1.5", 'Separation:', pile);
        this.add_button("Build", this.pile.bind(this), pile);

        const fence = this.add_fieldset("Fence", construct);
        this.add_numeric_input('posts', "2", 'Posts:', fence);
        this.add_numeric_input('fenceSeparation', "4.0", 'Separation:', fence);
        this.add_numeric_input(
            'turnDegrees', "10.0", 'Deviation (degrees):', fence);
        this.add_numeric_input('height', "3.0", 'Height:', fence);
        this.add_numeric_input(
            'spinDegrees', "240.0", 'Spin (degrees):', fence);
        this.add_button("Build", this.fence.bind(this), fence);

        const constructButtons = this.append_node('div', undefined, construct);
        this.add_button("Drop", this.drop.bind(this), constructButtons);
        this.add_button(
            "Stop build", this.stop_build.bind(this), constructButtons);
        this.add_button(
            "Stop spinning", this.stop_spinning.bind(this), constructButtons);
        this.add_button("Clear", this.clear.bind(this), constructButtons);

        this._cameraControls.show(this.add_fieldset("Camera"));
 
        const cursor = this.add_fieldset("Cursor");
        this.add_tickbox('trackBuild', "Track build", cursor);
        this.cursorInput = this.add_cursor_panel(cursor);
        this.get_cursor_subject();

        const monitor = this.add_fieldset("Monitor");
        this.add_button("Clear", this.monitor_clear.bind(this), monitor);
        this.add_button("Fetch /", this.get_monitor.bind(this), monitor);
        const progressNode = this.append_node('span', undefined, monitor);
        progressNode.setAttribute('id', 'progress');
        this.progressTextNode = this.append_node(undefined, "", progressNode);
        const fetchCountNode = this.append_node('div', undefined, monitor);
        this.fetchCountTextNode = this.append_node(
            undefined, "", fetchCountNode);
        this.monitor = this.append_node('pre', undefined, monitor);
        
        return this;
    }
}
UserInterface.methodList = ["get", "put", "patch", "delete"];
UserInterface.cursorSubjectPath = ['root', 'cursors', 0, 'subjectPath'];
