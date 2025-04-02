const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
    },
});

io.on("connection", (socket) => {
    console.log("A user connected");

    socket.on("biometric_verified", (data) => {
        console.log("Biometric Verified for Voter:", data.voter_id);
        socket.emit("vote_ready", { voter_id: data.voter_id });
    });

    socket.on("vote_cast", (data) => {
        console.log("Vote Received for Candidate:", data.candidate_id);
        io.emit("vote_received", { candidate_id: data.candidate_id });
    });

    socket.on("disconnect", () => {
        console.log("A user disconnected");
    });
});

const PORT = 8080;
server.listen(PORT, "0.0.0.0", () => {
    console.log(`Socket.io Server Running on http://0.0.0.0:${PORT}`);
});
