importScripts("https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js");
importScripts(
  "https://www.gstatic.com/firebasejs/8.10.1/firebase-messaging.js"
);

firebase.initializeApp({
  apiKey: "AIzaSyB090AN9M_H_WLhdbusUtKta25z_wyOQOI",
  authDomain: "freelancer-45e71.firebaseapp.com",
  projectId: "freelancer-45e71",
  messagingSenderId: "1045799017090",
  appId: "1:1045799017090:web:dfa165f369baa27614729b",
  measurementId: "G-Q3FC5BYMSS",
});

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function (payload) {
  const notification = payload.notification;
  const options = {
    body: notification.body,
    icon: notification.icon,
  };
  return self.registration.showNotification(notification.title, options);
});

