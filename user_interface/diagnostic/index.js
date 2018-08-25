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
        this._interval = undefined;
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
    
    stop() {
        if (this._interval !== undefined) {        
            clearInterval(this._interval);
            this._interval = undefined;
        }
        fetch(this.api_path(['root', 'gameObjects']), {"method": "DELETE"})
        .then(() => {
            this.add_results("Stopped.");
        });
    }
    
    reset() {
        if (this._interval !== undefined) {        
            clearInterval(this._interval);
            this._interval = undefined;
        }
            
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
        
        let xIndex = 0;
        let yIndex = 0;
        let zIndex = 0;
        
        let finished = false;
        function add_one(that) {
            if (finished) {
                console.log("Finished.");
                return;
            }
            that.put({
                    "rotation": [0, 0, 0],
                    "worldPosition": [x, y, z],
                    "physics": false
                }, 'root', 'gameObjects', objectIndex)
            .then(() => {
                objectIndex += 1;
    
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
                            finished = true;
                        }
                    }
                }
                
                if (finished) {
                    clearInterval(that._interval);
                    that.get()
                    .then(response => {
                        that.add_results(response);
                        for(var index=0; index<objectIndex; index++) {
                            that.put(true,
                                     'root', 'gameObjects', index, "physics");
                        }
                    });
                }
            });
        }
        fetch(this.api_path(['root', 'gameObjects']), {"method": "DELETE"})
        .then(() => {
            this._interval = setInterval(add_one, 100, this);
        });

        // Camera 12, 1, 7.

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
        this.add_button("Reset", this.reset.bind(this));
        this.add_button("Stop", this.stop.bind(this));
        
        this.results = this.appendNode('pre');
        
        return this;
    }
}

function main(userInterfaceID) {
    const userInterface = new UserInterface(userInterfaceID);
    return userInterface.show();
}