var mongoose = require('mongoose');
var express = require('express');
var router = express.Router();

var Schema = mongoose.Schema;

var photoSchema = new Schema({

  path:  { type: String },
  caption: { type: String }
  });


var Image = module.exports = mongoose.model('Photos', photoSchema);
router.getImages = function(callback, limit) {
 
 Image.find(callback).limit(limit);
}
 
 
router.getImageById = function(id, callback) {
  
 Image.findById(id, callback);
 
}

module.exports = router;