// (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
// Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver

import UserInterface from './UserInterface.js';

document.body.onload = () => {
    const userInterface = new UserInterface("user-interface");
    userInterface.show();
};
