'use strict';

var map_of_jobs = angular.module('map_of_jobs', ['ngMap', 'angularUtils.directives.dirPagination']);

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

	$scope.table_columns = ['Street', 'Zipcode']
	$scope.table_results = {'street': '123 fun street', 'Zipcode': '12345'}

	$http({url:'map_data', method:"GET"}).then(function(map_data){
		console.log(map_data);
	});

	$scope.search = {
		test: ["1","2"],
		results: [
				{address: '50 bobby lane', zipcode: 12345},
				{address: '51 bobby lane', zipcode: 12346},
				{address: '52 bobby lane', zipcode: 12347}
		],
		submit: function() {
			$scope.search.results.push({
				address: $scope.street,
				city: $scope.city,
				zipcode: $scope.zip
			});

			// toggle results div class
			$scope.showing_results = true;
		}


	}
})

