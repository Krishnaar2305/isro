const express = require('express');
const apiRoutes = require('./routes/apiRoutes');
const app = express();

app.set("view engine", "ejs");
const currDir = process.cwd();
console.log(currDir)
app.set("views", `${currDir}/views`);
app.use(express.static('./public'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json({ limit: "1mb" }));

app.use("/api", apiRoutes);

app.use("/", (req, res) =>{
    res.render("index")

});


// const dbURI = "your_mongoDB_connection_string_here";

// mongoose.connect(dbURI)
// .then(result => {
app.listen(3000, () => {
    console.log("Listening for requests on port 3000");
});
// });
