var express   = require('express');
var router    = express.Router();
var upload    = require('./upload');
var mongoose  = require('mongoose');
var photo     = require('../models/Photo')
var Photo     = mongoose.model('Photos');
var spawn     = require("child_process").spawn;
var execSync  = require('child_process').execSync;
var fs        = require('fs');
var window    = require('window');
var ObjectId = require('mongodb').ObjectID;
var global = {}


/* GET home page. */
router.get('/', function(req, res) {

    Photo.find({}, ['_id', 'path', 'caption'], {sort:{ _id: -1} }, function(err, photos) {
        res.render('index', { title: 'Image Classification with Inception, NodeJS, mongoDB', 
                             msg:req.query.msg, 
                             photolist : photos
                            });
    });
});



router.get('/images', function(req, res) {
//calling the function from index.js class using routes object..
	photo.getImages(function(err, genres) {
		if (err) {
			throw err;
		}

		res.json(genres);
	});

});


router.get('/images/delete/:id', function(req, res) {
    photo.getImageById(req.params.id, function(err, genres) {
    var id = genres._id;
    Photo.remove({_id: ObjectId(id)}, function(err, result) {
    if (err) return console.log(err);
    console.log(req.body);
    res.redirect('/');
  });
});
});

//router.get('/images/deleteall', function(req, res) {
//    photo.getImages();
//    Photo.deleteMany();
//    res.redirect('/images');
//});


router.get('/result', function(req, res){
    Photo.findOne({}, ['path','caption'], {sort:{ _id: -1}}, function(err, photos){
        
        res.render('result', {
            photolist: photos, 
            cls: global.cls, 
            score: global.score});
       });
    });
    


/** Upload file to path and add record to database */

router.post('/upload', function(req, res) {
    upload(req, res,function(error) {
      if(error){
         res.redirect('/?msg=3');
      }else{
        if(req.file == undefined){
          
          res.redirect('/?msg=2');

        }else{
             
            /**
             * Create new record in mongoDB
             */
            var fullPath = "files/"+req.file.filename;

            var str = execSync('python ./MLmodel/inception_client.py --server=35.196.81.176:9000 --image=./public/' + fullPath, { encoding: 'utf8' });
            var cls = str.match(/Predicted Class: (.*)\nPredicted Score/)[1]
            var score = str.match(/Predicted Score: (.*)/)[1];
            global.cls = cls;
            global.score = score;
            
//            console.log(str)
//            console.log(cls)
//            console.log(score)
//            res.send("Successfully Uploaded and Analyze!" + str)
            res.redirect('/result')
            
            
            var document = {
              path:     fullPath, 
              caption:  [cls + ", " + score]
            };
  
          var photo = new Photo(document); 
          photo.save(function(error){
            if(error){ 
              throw error;
            }
//            var pyProg = spawn('python', ['./MLmodel/inception_client.py', '--server=35.196.81.176:9000', '--image=' + './public/' + fullPath]);
//            pyProg.stdout.on('data', function (data) {
//                res.send(data.toString());
//          
//           });
            
          });
      }
    }
  });    
});




// router.get('/test', function(req, res) {


//     var pyProg = spawn('python', ['./MLmodel/inception_client.py', '--server=35.224.246.197:9000', '--image=' + './public/' + fullPath]);
//     pyProg.stdout.on('data', function (data) {
//     res.send(data.toString());
//   });

// });




module.exports = router;
