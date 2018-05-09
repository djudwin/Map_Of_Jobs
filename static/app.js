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
		console.log('hi')
	};

	$http({url:'map_data', method:"GET"}).then(function(map_data){
		console.log(map_data);
	});

	$scope.search = {
		submit: function() {
			var results = [
				{address: '50 bobby lane', zipcode: 12345},
				{address: '51 bobby lane', zipcode: 12345},
				{address: '52 bobby lane', zipcode: 12345}
			];

			$scope.search.results = results;


			// toggle results div class
			$scope.showing_results = true;
		}
	}
})

