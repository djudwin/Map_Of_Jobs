'use strict';

var map_of_jobs = angular.module('map_of_jobs', ['ngMap', 'angularUtils.directives.dirPagination']);

map_of_jobs.controller('map_of_jobs_controller', function($scope, $http, $window, NgMap) {
    NgMap.getMap().then(function (map) {
        console.log(map.getCenter());
        console.log('markers', map.markers);
        console.log('shapes', map.shapes);
    });


    $scope.googleMapsUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAnGj_CJuLQjEjd94i0MOvQVB4FDLRpdec";



    $scope.search = {
        test: ["1", "2"],
        results: []};
    $scope.search.results.push({});

    // toggle results div class
	$scope.showing_results = true;

	$scope.table_columns = ['type','address', 'city', 'state','zip','beds','baths','price','size','crimes'];
	$scope.table_results = []; //{'street': '123 fun street', 'Zipcode': '12345'};


	$scope.townhouse = 0;
	$scope.house = 0;
	$scope.condo = 0;
	$scope.beds = 0;
	$scope.baths = 0;
	$scope.location = "";
	$scope.rating = 0;
	$scope.size = 0;
	$scope.rating = 1;
	$scope.price = "0,100000";

    $scope.submit_button = function () {


        var data = {
            'location': $scope.location,
            'townhouse': $scope.townhouse,
			'house': $scope.house,
			'condo': $scope.condo,
            'rating': $scope.rating,
            'price': $scope.price,
            'beds': $scope.beds,
            'baths': $scope.baths,
            'size': $scope.size
        };


        /*$http({url: 'map_data', method: "GET",param: data}).then(function (map_data) {
        	console.log(map_data);
    	});*/

        $http({
            url: '/get_data',
            method: "POST",
            data: JSON.stringify(data),
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        }).then(function (data) {
            //console.log(data);
			console.log(data);
			$scope.table_results = [];
			if(data.data.length === 0){
			    $scope.table_results.push({'type':'No Results'})
            }

            for (var i = 0; i < data.data.length; i++){
            	$scope.table_results.push({'type':data.data[i]['type'],
											'address':data.data[i]['address'],
											'city':data.data[i]['city'],
											'state':data.data[i]['state'],
											'zip':data.data[i]['postal_code'],
											'beds': data.data[i]['beds'],
											'baths':data.data[i]['baths'],
											'price':data.data[i]['price'],
											'size':data.data[i]['size'],
											'crimes':data.data[i]['crimes'],
                                            'latitude':data.data[i]['lat'],
                                            'longitude':data.data[i]['long']}
											);
            }

			$scope.showing_results = true;
        });


    }

});