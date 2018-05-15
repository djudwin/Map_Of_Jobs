'use strict';
var mymap;
var map_of_jobs = angular.module('map_of_jobs', ['ngMap', 'angularUtils.directives.dirPagination']);



map_of_jobs.controller('map_of_jobs_controller', function($scope, $http, $window, NgMap) {
    $scope.mymarkers = [];
    NgMap.getMap().then(function (map) {
        console.log(map.getCenter());
        console.log('markers', map.mymarkers);
        console.log('shapes', map.shapes);
        mymap = map;

    });
    /*function initialize() {
        var mapProp = {
            center: new google.maps.LatLng(38, -78),
            zoom: 6,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById('map'), mapProp);
    }*/
    //var infowindow = new google.maps.InfoWindow({});

	//var marker, i;

	/*for (i = 0; i < mymarkers.length; i++) {
		marker = new google.maps.Marker({
			position: new google.maps.LatLng(locations[i][1], locations[i][2]),
			map: map
		});

		google.maps.event.addListener(marker, 'click', (function (marker, i) {
			return function () {
				infowindow.setContent(locations[i][0]);
				infowindow.open(map, marker);
			}
		})(marker, i));
	}
	*/


    $scope.googleMapsUrl = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAnGj_CJuLQjEjd94i0MOvQVB4FDLRpdec";
    // toggle results div class
	$scope.showing_results = true;

	$scope.table_columns = ['type','address', 'city', 'state','zip','beds','baths','price','size','crimes','latitude','longitude'];
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
        var markers = [];

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
            var lat = 0;
            var long = 0;
            for (var i = 0; i < data.data.length; i++) {
                $scope.table_results.push({
                        'type': data.data[i]['type'],
                        'address': data.data[i]['address'],
                        'city': data.data[i]['city'],
                        'state': data.data[i]['state'],
                        'zip': data.data[i]['postal_code'],
                        'beds': data.data[i]['beds'],
                        'baths': data.data[i]['baths'],
                        'price': data.data[i]['price'],
                        'size': data.data[i]['size'],
                        'crimes': data.data[i]['crimes'],
                        'latitude': data.data[i]['lat'],
                        'longitude': data.data[i]['long']
                    }
                );
                lat += parseFloat(data.data[i]['lat']);
                long += parseFloat(data.data[i]['long']);
                var address = data.data[i]['address'] + ', ' + data.data[i]['city'] + ', ' + data.data[i]['state'] + ', ' + data.data[i]['postal_code'];
                var marker = new google.maps.Marker({
                    position: new google.maps.LatLng(parseFloat(data.data[i]['lat']), parseFloat(data.data[i]['long'])),
                    map: mymap,
                    draggable: false,
                    content: address,
                    animation: google.maps.Animation.DROP

                });
                (function (marker, data) {
                    google.maps.event.addListener(marker, 'click', function() {

                        new google.maps.InfoWindow({content: marker.content}).open(mymap,marker);
                    });
                })(marker, data);

            }
            lat /= data.data.length;
            long /= data.data.length;
            mymap.panTo(new google.maps.LatLng(lat,long));
            mymap.setZoom(12);
            //console.log(map.mymarkers);
			$scope.showing_results = true;
        });

    }

});