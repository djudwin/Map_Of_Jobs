'use strict';

var map_of_jobs = angular.module('map_of_jobs', ['ngMap']);

map_of_jobs.controller('map_of_jobs_controller', function($scope, $http, $window, NgMap) {
	NgMap.getMap().then(function(map) {
    console.log(map.getCenter());
    console.log('markers', map.markers);
    console.log('shapes', map.shapes);
  });

	$scope.googleMapsUrl="https://maps.googleapis.com/maps/api/js?key=AIzaSyAnGj_CJuLQjEjd94i0MOvQVB4FDLRpdec";

	$scope.populateMap = function(){

	};

	$http({url:'map_data', method:"GET"}).then(function(map_data){
		console.log(map_data);
	});
});


