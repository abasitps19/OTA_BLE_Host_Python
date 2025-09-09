
<a id="readme-top"></a>




# STM32 OTA Host 
## Interfaces

  1. COM Port (optional)
  2. BLE

## Getting Started

<!-- TABLE OF CONTENTS -->


<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#setup-venv">Installation</a></li>
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

OTA host with Interfaces BLE and UART 

Use the `BLANK_README.md` to get started.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->

## Getting Started

### Installation

open termianl and eenter follwoing command.



Install python >3.8

1. Install python >3.8
2. * virtual environment 
  ```sh
  python -m venv venv
  ```

3. Activate ota_host_venv
 ```sh
  .\venv\Scripts\activate
  ```

4. install serial port 
 ```sh
  pip install pyserial 
 ```
5. show pyserial
  ```sh
   pip show pyserial
  ```  
  Expected output
  ```text
   Version: 3.5
   Summary: Python Serial Port Extension
   Home-page: https://github.com/pyserial/pyserial
```

6. check available com port 
  ```sh
   python -m serial.tools.list_ports
  ```
7. output example.
  ```text
    COM1
    COM7
  ``` 


8. verify the installation   
  ```sh
   pip list
  ```
9. install BLE related packages
 ```sh
  pip install bleak
  ```
```sh
  pip install asyncio
  ```
```sh
  pip install rich  
  ```


10. Virtual Environment Management Commands 
     <!-- Exit the virtual environment-->
```sh
  deactivate	
```
  <!-- Save dependencies to file-->
```sh
  pip freeze > requirements.txt   
```
Install from requirements file
<!-- Install from requirements file-->
```sh
  pip install -r requirements.txt   
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Installation Summary
1. Virtual Environment Management Commands: python -m venv stmota_vnv
2. Activate virtual environment command  .\stmota_vnv\Scripts\activate
  * it should appear on termainal like: (stmota_vnv) PS *  E:\project\STM32\stm32_ota_host\ota_host_python>
3. Install serial terminal command: pip install pyserial
4. check com port by command on terminal, command: python -m serial.tools.list_ports
   output example: 
   COM1
   COM7    
5. Install BLE related libraries:  bleak, asyncio, rich
      
6. references: 
  * Getting Started with Python in VS Code (channel# "Visual Studio Code" ) https://www.youtube.com/watch?v=D2cwvpJSBX4
  * Python serial port communication using PySerial (channel# "Avirup Basu" ) https://www.youtube.com/watch?v=Kr1RyK6WENQ
 
  
