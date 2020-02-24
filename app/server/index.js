var dotenv = require('dotenv').config();
console.log(`my mongo uri is: ${process.env.MONGO_URI}`);

const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const HTTPS = require("https");
const FS = require("fs");
const UUID = require("uuid");
const session = require("express-session");
const app = express();

// Middleware
app.use(
  session({
    secret: "scout6482327459489835149786149",
    cookie: {
      secure: true,
      maxAge: 60000
    },
    saveUninitialized: true,
    resave: true
  })
);

app.use(bodyParser.json());
app.use(
  bodyParser.urlencoded({
    extended: true
  })
);

app.get("/session", (request, response, next) => {
  request.session.example = UUID.v4();
  response.send({
    id: request.session.example
  });
});


app.get("/details", (request, response, next) => {
  // request.session.example = UUID.v4();
  response.send(JSON.parse(FS.readFileSync(`${__dirname}/currentJSON.json`, 'utf8')));
});


app.post("/session", (request, response, next) => {
  if (request.body.session != request.session.example) {
    return response.status(500).send({
      message: "The data in the session does not match!"
    });
  }
  response.send({
    message: "Success!"
  });
});



app.post("/honk", (request, response, next) => {
  if (request.body.session != request.session.example) {
    return response.status(500).send({
      message: "The data in the session does not match!"
    });
  }
  response.send({
    message: "Success!"
  });
  console.log(`should honk now`);
});


app.use(
  cors({
    origin: ["https://10.6.6.13:8080"],
    credentials: true
  })
);

HTTPS.createServer({
    key: FS.readFileSync("server.key"),
    cert: FS.readFileSync("server.cert")
  },
  app
).listen(443, () => {
  console.log("Listening at :443...");
});


// app.use(cors());

const plates = require("./routes/api/plates");
const faces = require("./routes/api/faces");
const drives = require("./routes/api/drives");
const polls = require("./routes/api/polls");
const geocodes = require("./routes/api/geocodes");
const dirp = require("./routes/api/dirp");

app.use("/api/plates", plates);
app.use("/api/faces", faces);
app.use("/api/drives", drives);
app.use("/api/polls", polls);
app.use("/api/geocodes", geocodes);
app.use("/api/dirp", dirp);

app.get("/thumb/:type/:fileName", (request, response, next) => {
  if (request.body.session != request.session.example) {
    return response.status(500).send({
      message: "The data in the session does not match!"
    });
  }

  if (request.params.type === 'face') {
    var filepath = `/tesladrive/detections/faces/${request.params.fileName}`
    console.log(`FILEPATH:${filepath}`);

    response.sendFile(filepath);
    console.log(`should return face thumbnail now`);
  } else if (request.params.type === 'plate') {
    var filepath = `/tesladrive/detections/vehicles/${request.params.fileName}`
    console.log(`FILEPATH:${filepath}`);

    response.sendFile(filepath);
    console.log(`should return face thumbnail now`);
  }


});

app.get("/image/:type/:fileName", (request, response, next) => {
  if (request.body.session != request.session.example) {
    return response.status(500).send({
      message: "The data in the session does not match!"
    });
  }


  if (request.params.type === 'face') {
    var filepath = `/tesladrive/detections/people/${request.params.fileName}`
    console.log(`FILEPATH:${filepath}`);

    response.sendFile(filepath);
    console.log(`should return face thumbnail now`);
  } else if (request.params.type === 'plate') {
    var filepath = `/tesladrive/detections/vehicles/${request.params.fileName}`
    console.log(`FILEPATH:${filepath}`);

    response.sendFile(filepath);
    console.log(`should return face thumbnail now`);
  }


});

app.get("/video/:fileName", (request, response, next) => {
  if (request.body.session != request.session.example) {
    return response.status(500).send({
      message: "The data in the session does not match!"
    });
  }


  var filepath = `/tesladrive/Videos/${request.params.fileName}`
  console.log(`FILEPATH:${filepath}`);

  response.sendFile(filepath);


});



// Handle production
if (process.env.NODE_ENV === "production") {
  // Static folder
  app.use(express.static(__dirname + "/public/"));

  // Handle SPA
  app.get(/.*/, (req, res) => res.sendFile(__dirname + "/public/index.html"));
}

const port = process.env.PORT || 5000;

app.listen(port, () => console.log(`Server started on port ${port}`));