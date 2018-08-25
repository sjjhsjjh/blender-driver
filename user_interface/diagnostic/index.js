// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

class UserInterface {
    createNode(tag, text) {
        var element = document.createElement(tag);
        if ( text !== undefined ) {
            element.appendChild(document.createTextNode(text));
        }
        return element;
    }
    
    appendNode(tag, text, parent) {
        if (parent === undefined) {
            parent = this.userInterface;
        }
        return parent.appendChild(this.createNode(tag, text));
    }
    
    add_button(text, boundMethod) {
        const button = this.appendNode('button', text);
        button.setAttribute('type', 'button');
        button.onclick = boundMethod;
    }
    
    add_results(...objects) {
        objects.forEach(item => 
            this.results.insertBefore(
                document.createTextNode(JSON.stringify(item, null, "  ")),
                this.results.firstChild)
        );
        this.results.normalize();
    }
    
    clear_results() {
        while(true) {
            const child = this.results.firstChild;
            if (child === null) {
                break;
            }
            this.results.removeChild(child);
        }
    }

    constructor(userInterfaceID) {
        this._timeOut = undefined;
        this.userInterface = document.getElementById(userInterfaceID);
    }
    
    api_path(path) {
        return ['api', ...path].join('/');
    }
    
    put(value, ...path) {
        return fetch(this.api_path(path), {
           "method": "PUT",
           "body": JSON.stringify(value)
        });
    }
    
    build() {
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

        // Following code is based on a time out, but used to be based on an
        // interval. The interval seems more conceptually correct, but the time
        // out ensures that the above variables get incremented in
        // synchronisation with the PATCH requests. If they get out of
        // synchronisation, then an objectIndex can be duplicated and skipped,
        // like 8 goes twice and 9 is skipped.
        let phase = 2;
        function add_one(that) {
            const patch = (phase === 2) ?
                {
                    "rotation": [0, 0, 0],
                    "worldPosition": [x, y, z],
                    "physics": false
                } : {
                    "physics": true
                };
            fetch(that.api_path(['root', 'gameObjects', objectIndex]), {
                "method": "PATCH",
                "body": JSON.stringify(patch)
            })
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
                    that.get().then(response => that.add_results(response));
                }
                else {
                    
                    this._timeOut = setTimeout(
                        add_one, (phase === 2 ? 10 : 1), that);
                }
            });
        }
        this.reset().then(() => add_one(this));

        // Camera 12, 1, 7.

    }
    
    reset() {
        if (this._timeOut !== undefined) {        
            clearTimeout(this._timeOut);
            this._timeOut = undefined;
        }
        return fetch(this.api_path(['root', 'gameObjects']),
                     {"method": "DELETE"});
    }
    
    stop() {
        this.reset().then(() => this.add_results("Stopped."));
    }
    
    get(...path) {
        return fetch(this.api_path(path)).then(response => response.json());
    }
    
    get_camera() {
        this.get('root', 'camera').then(response => {
            this.add_results(response);
            if (response.subjectPath) {
                this.get(...response.subjectPath).then(response2 => {
                    console.log('subject', response2);
                });
            }
        });
    }
    
    get_root() {
        this.get().then(response => this.add_results(response));
    }
    
    put_animation() {
        this.put(
            {
                "valuePath": ["root", "camera", "orbitDistance"],
                "targetValue": 1.0,
                "speed": 1.0
            },
            'animations', 'ui', 'zoom'
        ).then(response => {
            console.log('put', response);
        });
    }
    
    show() {
        this.add_button("Fetch camera", this.get_camera.bind(this));
        this.add_button("Zoom", this.put_animation.bind(this));
        this.add_button("Fetch /", this.get_root.bind(this));
        this.add_button("Clear", this.clear_results.bind(this));
        this.add_button("Build", this.build.bind(this));
        this.add_button("Stop", this.stop.bind(this));
        
        this.results = this.appendNode('pre');
        
        return this;
    }
}

function main(userInterfaceID) {
    const userInterface = new UserInterface(userInterfaceID);
    return userInterface.show();
}