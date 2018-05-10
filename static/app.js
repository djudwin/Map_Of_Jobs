'use strict';

var map_of_jobs = angular.module('map_of_jobs', ['ngMap', 'angularUtils.directives.dirPagination']);

map_of_jobs.controller('map_of_jobs_controller', function($scope, $http, $window, NgMap) {
    NgMap.getMap().then(function (map) {
        // console.log(map.getCenter());
        // console.log('markers', map.markers);
        // console.log('shapes', map.shapes);
    });

    $scope.googleMapsUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAnGj_CJuLQjEjd94i0MOvQVB4FDLRpdec";

    $scope.populateMap = function () {
        console.log('hi')
    };

    $scope.table_columns = ['Street', 'Zipcode'];
    $scope.table_results = {'street': '123 fun street', 'Zipcode': '12345'};


    $scope.search = {
        test: ["1", "2"],
        results: [
            {"address": '50 bobby lane', "postal_code": 12345},
			{"address": '51 bobby lane', "postal_code": 12346},
			{"address": '52 bobby lane', "postal_code":12347}
			]};
    	$scope.search.results.push({});

    	// toggle results div class
    	$scope.showing_results = true;

	$scope.townhouse = 0;
	$scope.house = 0;
	$scope.condo = 0;
	$scope.beds = 0;
	$scope.baths = 0;
	$scope.location = "";
	$scope.rating = 0;
	$scope.size = 0;
	$scope.price = "0,50000";

    $scope.submit_button = function () {
        $scope.types = [];
        $scope.types[0] = 'unknown';
        var i = 1;
        if ($scope.townhouse == 1) {
            $scope.types[i] = 'Townhouse';
            i++;
        }
        if ($scope.house == 1) {
            $scope.types[i] = 'House';
            i++;
        }
        if ($scope.condo == 1) {
            $scope.types[i] = 'Condo';
        }


        var data = {
            'location': $scope.location,
            'townhouse': $scope.townhouse,
			'house': $scope.house,
			'condo': $scope.condo,
            'rating': parseInt($scope.rating),
            'price': $scope.price,
            'beds': $scope.beds,
            'baths': $scope.baths,
            'size': $scope.size
        };

/*
        $http({url: 'map_data', method: "GET",param: data}).then(function (map_data) {
        	console.log(map_data);
    	});
*/
        $http({
            url: '/get_data',
            method: "POST",
            data: JSON.stringify(data),
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        }).then(function (result) {
            console.log(result)
			$scope.search.results = result.data;
			$scope.showing_results = true;
        });


    }

});