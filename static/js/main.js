var labelusername = document.getElementById("label-username");
var inputusername = document.getElementById("username-input");
var btnjoin = document.getElementById("btn-join");
var mapPeers = { };
btnjoin.addEventListener("click", function () {
  if (inputusername.value.trim() === "") {
    labelusername.classList.add("text-danger");
    labelusername.textContent = "Username cannot be empty";
  } else {
    labelusername.classList.remove("text-danger");
    username = inputusername.value.trim();
    // Proceed with the join action
    console.log("Joining with username:", inputusername.value);
    inputusername.value = "";
    inputusername.disabled = true;
    inputusername.getElementsByClassName.visiblility = "hidden";
    btnjoin.disabled = true;
    btnjoin.style.visibility = "hidden";
    labelusername.textContent = "Username: " + username;
    var loc = window.location;
    var wsStart = "ws://";
    if (loc.protocol === "https:") {
      wsStart = "wss://";
    }
    var endpoint = wsStart + loc.host + "/ws" + loc.pathname;
    websocket = new WebSocket(endpoint);
    websocket.onopen = function (event) {
      console.log("WebSocket connection established");
    sendsignal('new-peer', {} )
    };
    websocket.onmessage = function (event) {
      var data = JSON.parse(event.data);
      var peerusername = data["peer"];
      var action = data["action"];
        if (action == peerusername) {
            return;
        }
        var receive_channel_name = data["message"]["receive_channel_name"];
        if(action == 'new-peer') {
            console.log("New peer joined:", peerusername);
            createOfferer(peerusername, receive_channel_name);
            // Handle new peer joining logic here
            return;
        }
        if(action == 'new-offer'){
            var offer = data['message']['sdp']
            createAnswerer(offer,peerusername,receive_channel_name)
        }
        if(action == 'new-answer'){
             var answer = data['message']['sdp']
             var peer = mapPeers[peerusername][0]
             peer.setRemoteDescription(answer)
             return;
        }
      // Handle incoming messages here
    };
    websocket.onclose = function (event) {
      console.log("WebSocket connection closed:", event);
    };
    websocket.onerror = function (event) {
      console.error("WebSocket error:", event);
    };
    console.log(endpoint);
  }
});

let localstream = new MediaStream();
const constraints = {
  audio: true,
  video:true
};
const localvideo = document.getElementById("local-video");
const btnToggleAudio = document.getElementById('btn-toggle-audio')
const btnToggleVideo = document.getElementById('btn-toggle-video')
let usermedia  = navigator.mediaDevices.getUserMedia(constraints)
    .then(function (stream) {
        localstream = stream;
        localvideo.srcObject = localstream;
        localvideo.mute = true; // Mute the local video
        var audioTracks = stream.getAudioTracks()
        var videoTracks  = stream.getVideoTracks()
        audioTracks[0].enabled = true
        videoTracks[0].enabled = true
        btnToggleAudio.addEventListener('click',()=>{
            audioTracks[0].enabled  = !audioTracks[0].enabled
            if(audioTracks[0].enabled){
                btnToggleAudio.innerHTML='Audio Mute'
                return;
            }
            btnToggleAudio.innerHTML = 'Audio Unmute'
        })
        btnToggleVideo.addEventListener('click',()=>{
            videoTracks[0].enabled  = !videoTracks[0].enabled
            if(videoTracks[0].enabled){
                btnToggleVideo.innerHTML='Video off'
                return;
            }
            btnToggleVideo.innerHTML = 'Video on'
        })
    })
    .catch(function (error) {
        console.error("Error accessing media devices.", error);
    });
var messageList = document.getElementById("message-list");
var btnsendmsg = document.getElementById('btn-send-msg') 
var msginput = document.getElementById('msg')
btnsendmsg.addEventListener('click',()=>{
    var msg = msginput.value
    var li = document.createElement('li')
    li.appendChild(document.createTextNode('me: '+ message))
    messageList.appendChild(li)
    var datachannels = getDataChannels();
    message = username + ': '+ message
    for(index in datachannels){
        datachannels[index].send(message)
    }
    msginput.value=' '
})
function sendsignal(action, data) {
    var jsondata = {
        'peer': username,
        action: action,
        message: data
    };
     websocket.send(JSON.stringify(jsondata));
}

function createOfferer(peerusername, receive_channel_name) {
    var peer = new RTCPeerConnection();
    addLocalTracks(peer);
    var dc = peer.createDataChannel("channel");
     dc.onopen = function () {
        console.log("Data channel is open");
    };
    dc.onmessage = function (event) {
        var message = event.data; 
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(peerusername + ": " + message));
        messageList.appendChild(li); 
        console.log("Received message:", event.data);
    };
    var remoteVideo = createVideo(peerusername);
    setOnTrack(peer, remoteVideo);
    mapPeers[peerusername] = [peer, dc]; 
    peer.onicecandidate = function (event) {
       var iceconnectionstate = peer.iceConnectionState;
       if(iceconnectionstate === "disconnected" || iceconnectionstate === "failed" || iceconnectionstate === "closed") {
        delete mapPeers[peerusername];
          if (iceconnectionstate != "closed") {
            peer.close();
          }
          remoteVideo(remoteVideo); 
       }

    }; 
    peer.onicecandidate = function (event) {
        if (event.candidate) {
            console.log('new ice candidate:', json.stringify(peer.localDescription));
            return;
        }
        sendsignal('new-offer', {
            'sdp': peer.localDescription,
            'peerusername': peerusername,
            'receive_channel_name': receive_channel_name
        });
    }
    peer.createOffer().then(o=>peer.setLocalDescription(o))
    .then(function () {
        console.log("Offer created and set as local description");
    })

}

function addLocalTracks(peer) {
    localstream.getTracks().forEach(function (track) {
        peer.addTrack(track, localstream);
    });
    return;
    
}

function createAnswerer(offer,peerusername,receive_channel_name){
    var peer = new RTCPeerConnection();
    addLocalTracks(peer);
    
    var remoteVideo = createVideo(peerusername);
    setOnTrack(peer, remoteVideo);
    peer.ondatachannel = (e)=>{
         peer.dc = e.channel
        peer.dc.onopen = function () {
            console.log("Data channel is open");
        };
        peer.dc.onmessage = function (event) {
            var message = event.data; 
            var li = document.createElement("li");
            li.appendChild(document.createTextNode(peerusername + ": " + message));
            messageList.appendChild(li); 
            console.log("Received message:", event.data);
        };
        mapPeers[peerusername] = [peer, peer. dc]; 
    }
    peer.onicecandidate = function (event) {
       var iceconnectionstate = peer.iceConnectionState;
       if(iceconnectionstate === "disconnected" || iceconnectionstate === "failed" || iceconnectionstate === "closed") {
        delete mapPeers[peerusername];
          if (iceconnectionstate != "closed") {
            peer.close();
          }
          remoteVideo(remoteVideo); 
       }

    }; 
    peer.onicecandidate = function (event) {
        if (event.candidate) {
            console.log('new ice candidate:', json.stringify(peer.localDescription));
            return;
        }
        sendsignal('new-answer', {
            'sdp': peer.localDescription,
            'peerusername': peerusername,
            'receive_channel_name': receive_channel_name
        });
    }
    peer.setRemoteDescription(offer)
    .then(()=>{
        console.log("remote description is set for %s",peerusername)
        return peer.createAnswer();
    })
    .then(a=>{
        console.log('answer created')
        peer.setLocalDescription(a)
    })
}

function createVideo(peerusername) {
    var videocontainer = document.getElementById("video-container");
    var remoteVideo = document.createElement("video");
    remoteVideo.id = peerusername+"-video";
    remoteVideo.autoplay = true;
    remoteVideo.muted = true;
    remoteVideo.playsInline = true;
    var videoWrapper = document.createElement("div");
    videocontainer.appendChild(videoWrapper);
    videoWrapper.appendChild(remoteVideo);
    return remoteVideo
 }
function setOnTrack(peer, remoteVideo) {
    var remoteStream = new MediaStream();
    remoteVideo.srcObject = remoteStream;
    peer.ontrack = async function(event) {
        remoteStream.addTrack(event.track, remoteStream);
    };
}

function removeVideo(remoteVideo) {
    var videoWrapper= remoteVideo.parentNode;
    videoWrapper.parentNode.removeChild(videoWrapper);
    videocontainer.removeChild(remoteVideo);
}
function getDataChannels(){
    var datachannels = []
    for(peerusername in mapPeers){
        var datachannel = mapPeers[peerusername][1]
        datachannels.push(datachannel)

    }
    return datachannels;
}