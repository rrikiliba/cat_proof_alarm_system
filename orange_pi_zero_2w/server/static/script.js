var client;
var isArmed = false;

function onConnect() {
    client.subscribe('device/ack/webapp')
    client.subscribe('image/submit')
    client.subscribe('alarm/disarm')
    client.subscribe('alarm/sound')
    client.subscribe('alarm/rearm')
    console.log("Connected to broker");
    updateStatus('brokerStatus', true);
    var message = new Paho.MQTT.Message("webapp");
    message.destinationName = "device/online";
    client.send(message);
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("Connection lost: " + responseObject.errorMessage);
    }
    updateStatus('brokerStatus', false);
    updateStatus('alarmStatus', false);
    alert("Connection lost!");
}

function onMessageArrived(message) {
    if (message.destinationName === "alarm/disarm") {
        console.log("Alarm state: " + message.payloadString);
        isArmed = false;
        setButtonState();
    }
    else if(message.destinationName === "image/submit") {
        const image = document.createElement('image');
        const bytes = new Blob(message.payloadBytes);
        image.src = URL.createObjectURL(bytes);
        document.getElementById('imageConteiner').appendChild(image);
        onImageRecived();
    }
    else if(message.destinationName === "alarm/rearm") {
        document.getElementById('arm').disabled = false;
        isArmed = true;
        setButtonState();
    }
    else if(message.destinationName === "device/ack/webapp") {
        console.log("Device ack: " + message.payloadString);
        if (message.payloadString === '1') {
            updateStatus('alarmStatus', true);
        }else{
            isAlarmConnected('alarmStatus', false);
            //alert("Alarm is not connected");
        }
    }
}

function onImageRecived(){
    console.log("Image received");
    document.getElementById('callTheCops').style.display = 'block';
}

document.getElementById('brokerForm').addEventListener('submit', function(e) {
    e.preventDefault();    
    var brokerPassword = document.getElementById('brokerPassword').value;
    try {
        client = new Paho.MQTT.Client(window.location.hostname, Number(9001), "webapp");
        client.connect({
            onSuccess: function() {
                onConnect();
                console.log("Connected successfully");
            },
            onFailure: function (error) {
                alert("Connection failed: " + error.errorMessage);
                console.log("Connection failed: ", error.errorMessage);
            },
            userName: "admin",
            password: brokerPassword,
            keepAliveInterval: 0
        });
        client.onConnectionLost = function(responseObject) {
            console.log("Connection lost: ", responseObject.errorMessage);
            onConnectionLost(responseObject);
        };
        client.onMessageArrived = function(message) {
            onMessageArrived(message);
        };
    } catch (error) {
        console.error("Failed to connect to broker: ", error);
        alert("Failed to connect to broker: " + error.message);
    }
});

document.getElementById('togglePassword').addEventListener('click', function() {
    var passwordField = document.getElementById('brokerPassword');
    var passwordFieldType = passwordField.getAttribute('type');
    if (passwordFieldType === 'password') {
        passwordField.setAttribute('type', 'text');
    } else {
        passwordField.setAttribute('type', 'password');
    }
});

document.getElementById('arm').addEventListener('click', function() {
    if(!isArmed) {
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message("armed");
            message.destinationName = "alarm/rearm";
            client.send(message);
            console.log("Message sent: armed");
            isArmed = true;
            setButtonState();
        } else {
            console.log("Client is not connected");
            alert("Broker is not connected");
        }
    }else{
        if (client && client.isConnected()) {
            var message = new Paho.MQTT.Message("disarmed");
            message.destinationName = "alarm/disarm";
            client.send(message);
            console.log("Message sent: disarmed");
            isArmed = false;
            setButtonState();
        } else {
            console.log("Client is not connected");
            alert("Broker is not connected");
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    updateStatus('brokerStatus', false);
    updateStatus('alarmStatus', false);
});

function updateStatus(elementId, isConnected) {
    const element = document.getElementById(elementId);
    const passwordMessage = document.querySelector('.instruction');
    if (isConnected) {
        element.classList.add('connected');
        element.classList.remove('disconnected');
        element.textContent = `${elementId.replace('Status', ' status')}: Connected`;
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('brokerStatus').style.display = 'none';
        document.getElementById('systemStatus').style.display = 'block';
        passwordMessage.style.display = 'none';
    } else {
        element.classList.add('disconnected');
        element.classList.remove('connected');
        element.textContent = `${elementId.replace('Status', ' status')}: Disconnected`;
        document.getElementById('brokerForm').style.display = 'block';
        document.getElementById('arm').style.display = 'none';
        document.getElementById('systemStatus').style.display = 'none';
        passwordMessage.style.display = 'block';
    }
    checkSystemStatus();
}

function isAlarmConnected(elementId, isConnected) {
    const message = document.querySelector('.instruction');
    if(elementId === 'alarmStatus' && !isConnected){
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('brokerStatus').style.display = 'block';
        document.getElementById('systemStatus').style.display = 'block';
        document.getElementById('alarmStatus').style.display = 'block';
        message.textContent = "Wait for the alarm to connect to the broker";
        message.style.display = 'block';
    }
    else{
        updateStatus(elementId, isConnected);
    }
}

function setButtonState() {
    const arm = document.getElementById('arm');
    const alarmArmed = document.getElementById('alarmArmed');
    const message = document.querySelector('.instruction');
    if (isArmed) {
        arm.textContent = "Disarm";
        alarmArmed.textContent = "The alarm is armed";
        alarmArmed.classList.remove('disconnected');
        alarmArmed.classList.add('connected');
        message.style.display = 'none';
    } else {
        arm.textContent = "Arm";
        alarmArmed.textContent = "The alarm is disarmed";
        alarmArmed.classList.remove('connected');
        alarmArmed.classList.add('disconnected');
        message.style.display = 'none';
        document.getElementById('brokerForm').style.display = 'none';
        document.getElementById('arm').style.display = 'block';
    }
}


function checkSystemStatus() {
    const brokerConnected = document.getElementById('brokerStatus').classList.contains('connected');
    const alarmConnected = document.getElementById('alarmStatus').classList.contains('connected');
    const systemStatus = document.getElementById('systemStatus');
    const alarmArmed = document.getElementById('alarmArmed');
    alarmArmed.textContent = "The alarm is disarmed";
    alarmArmed.classList.add('status-box', 'disconnected');

    if (brokerConnected && alarmConnected) {
        systemStatus.textContent = "The alarm is on";
        systemStatus.classList.add('status-box', 'connected');
        document.getElementById('brokerStatus').style.display = 'none';
        document.getElementById('alarmStatus').style.display = 'none';
        document.getElementById('arm').style.display = 'block';
    } else {
        systemStatus.textContent = "";
        systemStatus.classList.remove('connected');
    }

}