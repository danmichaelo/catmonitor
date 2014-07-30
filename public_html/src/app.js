'use strict';

// Declare app level module which depends on filters, and services
angular.module('app', ['angularCharts']).

controller('AppCtrl', ['$scope', '$http', function($scope, $http) {

	$scope.projects = [];

  $http.get('./api').success(function(response) {
    $scope.projects = response.projects;
  });

}]);