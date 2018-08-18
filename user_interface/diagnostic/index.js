// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

class UserInterface {
    createNode(tag, text) {
        var element = document.createElement(tag);
        if ( text !== null ) {
            element.appendChild(document.createTextNode(text));
        }
        return element;
    }
    
    appendNode(tag, text, parent) {
        return parent.appendChild(this.createNode(tag, text));
    }

    constructor(userInterfaceID) {
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
    
    get(...path) {
        return fetch(this.api_path(path)).then(response => response.json());
    }
    
    get_camera() {
        this.get('root', 'camera').then(response => {
            console.log('camera', response);
            this.appendNode('pre',
                            JSON.stringify(response, null, "  "),
                            this.userInterface);
            if (response.subjectPath) {
                this.get(...response.subjectPath).then(response2 => {
                    console.log('subject', response2);
                });
            }
        });
    }
    
    get_root() {
        this.get().then(response => {
            console.log('root', response);
        });
    }
    
    put_animation() {
        this.put({
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
        this.button = this.appendNode('button', "Fetch camera", this.userInterface);
        this.button.setAttribute('type', 'button');
        this.button.onclick = this.get_camera.bind(this);
        
        this.button = this.appendNode('button', "Zoom", this.userInterface);
        this.button.setAttribute('type', 'button');
        this.button.onclick = this.put_animation.bind(this);
        
        this.button = this.appendNode('button', "Fetch /", this.userInterface);
        this.button.setAttribute('type', 'button');
        this.button.onclick = this.get_root.bind(this);
        
        return this;
    }
}

function main(userInterfaceID) {
    const userInterface = new UserInterface(userInterfaceID);
    return userInterface.show();
}