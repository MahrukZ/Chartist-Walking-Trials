const MAPBOX_API_KEY = "pk.eyJ1Ijoicnlhbml0byIsImEiOiJjazM2NGZtbmIwZTJuM2Nxanpsa2tlOWR5In0.EmeKG8ONjjFsgwaE5KSH7A";

$(function() {

  $.getJSON('/api/locations', function(data) {

    var map = L.map('map',
    {
      fullscreenControl: true,
      minZoom: 5
    }).setView([51.58678979599378, -2.9951691627502446], 16);

    var basemaps = [
      L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + MAPBOX_API_KEY, {
        maxZoom: 19,
      	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
      		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      		'Imagery &copy; <a href="https://www.mapbox.com/">Mapbox</a>',
      	id: 'mapbox.streets'
      }),
      L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/tiles/256/{z}/{x}/{y}?access_token=' + MAPBOX_API_KEY, {
        maxZoom: 19,
      	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
      		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      		'Imagery &copy; <a href="https://www.mapbox.com/">Mapbox</a>',
      	id: 'mapbox.satellite'
      })
    ];

    map.addControl(L.control.basemaps({
      basemaps: basemaps,
      tileX: 32222,  // tile X coordinate
      tileY: 21769,  // tile Y coordinate
      tileZ: 16   // tile zoom level
    }));

    let routes = [];
    data.forEach(function(row) {
      if (routes.includes(row['route']) == false) {
        routes.push(row['route']);
      }
    });

    for (i = 1; i <= routes.length; i++) {

      let name, color, icon_html;
      if (i == 1) {
        name = (lang == 'cy' ? "Llwybr Hawdd" : "Easy Route");
        color = '#007bff';
        icon_html = '<span class="star"></span>';
      } else if (i == 2) {
        name = (lang == 'cy' ? "Llwybr Anodd" : "Hard Route");
        color = 'red';
        icon_html = '<span class="star red"></span>';
      }

      // Salesman.js - https://github.com/lovasoa/salesman.js
      // Calculates the easiest route between all points on the map
      let points = []
      data.forEach(function(row) {
        if (row['route'] == i) {
          points.push(new Point(row['latitude'], row['longitude']));
        }
      });

      var solution = solve(points, 0.999999);
      var ordered_points = solution.map(i => points[i]);

      let waypoints = []
      ordered_points.forEach(function(point) {
          waypoints.push(L.latLng(point['x'], point['y']));
      });


      if(waypoints.length > 0) {

        // Loop back around to start of route
        waypoints.push(waypoints[0]);

        // Required to overcome the 25 co-ordinate limit per route
        let mapbox_limit = 24;
        let number_of_loops = Math.ceil((waypoints.length+1)/mapbox_limit);

        for (var i = 0; i < number_of_loops; i++) {

          let minimum, maximum;

          minimum = i * mapbox_limit;
          maximum = ((i+1) * mapbox_limit) + 1;

          if (i > 0) {
            name += (lang == 'cy' ? " (Ymhellach)" : " (Extended)");
          }

          let current_waypoints = waypoints.slice(minimum, maximum);

          L.Routing.control({
            waypoints: current_waypoints,
            draggableWaypoints: false,
            addWaypoints: false,
            fitSelectedRoutes: false,
            summaryTemplate: '<h2>' + icon_html + ' ' + name + '</h2><h3>{distance}, {time}</h3>',
            lineOptions: {
              styles: [{color: color, opacity: .5, weight: 6}]
            },
            createMarker: function(i, wp) {
      				return L.marker(wp.latLng, {
      					icon: L.divIcon({
                  html: icon_html,
                })
      				});
      			},
            router: L.Routing.mapbox(MAPBOX_API_KEY,
              {
                profile: 'mapbox/walking',
                // language: 'fr'
              })
            }
          ).addTo(map);

        }

      }

    }

    for (var i = 0; i < data.length; i++) {

      if (data[i]['name'] || data[i]['image'] || data[i]['description']) {

          let popup = "";

          if (data[i]['name']) {
            popup += '<strong>' + data[i]['name'] + '</strong><br>';
          }

          if (data[i]['description']) {
            popup += data[i]['description'] + '<br>';
          }

          if(data[i]['image']) {
            popup += '<a class="popup-link" href="' + data[i]['image'] + '"><img src="' + data[i]['image'] + '" alt="' + data[i]['name'] + '" class="popup-image"></a>';
          }

          //Leaflet marker code adapted from http://bl.ocks.org/mapsam/6175692
          L.marker(L.latLng(data[i]['latitude'], data[i]['longitude']),
          {icon: L.divIcon({
            html: '<span class="info"></span>',
            popupAnchor:  [5, -10]
          }, )})
          .addTo(map)
          .bindPopup(popup, {
            minWidth: 170,
            maxWidth: 170
          }).on('click', function (e) {
            $(".popup-link").magnificPopup({
              type: 'image',
              closeOnContentClick: true
            });
          });

      }

    }

    var marker, easyControl, hardControl;

    // Current location function adapted from code example at https://stackoverflow.com/a/40437622
    function onLocationFound(e) {

      // Remove the old marker and control (to update the user's location)
      if (marker) {
        map.removeLayer(marker);
      }
      if (easyControl) {
        easyControl.getPlan().setWaypoints([]);
      }
      if (hardControl) {
        hardControl.getPlan().setWaypoints([]);
      }

      let user_coords = [e.latitude, e.longitude];
      // fake location
      //let user_coords = [51.58974789344375, -2.99802303314209];
      let radius = parseInt(e.accuracy / 2);

      marker = L.marker(L.latLng(user_coords), {
        icon: L.divIcon({
          html: '<span class="pulse"></span>',
        }),
        popupAnchor:  [10, -10]
      }).addTo(map)
      .bindTooltip("<em>Within ~" + radius + "m</em>",
      {
        direction: 'bottom',
        className: 'current-location'
      });

      var nearest;

      nearest = nearestNeighbour(user_coords, data, 1);
      if(nearest != false) {

        // Displays a route to the nearest pavement roundel
        easyControl = L.Routing.control({
          waypoints: [user_coords, nearest],
          draggableWaypoints: false,
          addWaypoints: false,
          fitSelectedRoutes: false,
          show: false,
          containerClassName: 'hidden',
          lineOptions: {
            styles: [{color: '#007bff', opacity: .75, weight: 4, dashArray: '7, 7'}]
          },
          createMarker: function(i, wp) {
    				return L.marker(wp.latLng, {
    					icon: L.divIcon({
                html: '',
              })
    				});
    			},
          router: L.Routing.mapbox(MAPBOX_API_KEY,
            {
              profile: 'mapbox/walking'
            })
          }
        ).addTo(map);

      }

      nearest = nearestNeighbour(user_coords, data, 2);
      if(nearest != false) {

        hardControl = L.Routing.control({
          waypoints: [user_coords, nearest],
          draggableWaypoints: false,
          addWaypoints: false,
          fitSelectedRoutes: false,
          show: false,
          containerClassName: 'hidden',
          lineOptions: {
            styles: [{color: 'red', opacity: .75, weight: 4, dashArray: '7, 7'}]
          },
          createMarker: function(i, wp) {
    				return L.marker(wp.latLng, {
    					icon: L.divIcon({
                html: '',
              })
    				});
    			},
          router: L.Routing.mapbox(MAPBOX_API_KEY,
            {
              profile: 'mapbox/walking',
              // language: 'cy'
              // Welsh is not supported in Mapbox
            })
          }
        ).addTo(map);

      }

    }

    map.locate({
      watch: true
    });
    map.on('locationfound', onLocationFound);

    // Calculates the nearest neighbour for the user's location and a list of locations
    function nearestNeighbour(user_coords, locations, route = null) {

      var current_distance = 0;
      var nearest_distance = -1;
      var nearest = [];

      for (var i = 0; i < data.length; i++) {

        // Only for selected routes
        if (route != null) {
          if (locations[i]['route'] != route) {
            continue;
          }
        }

        current_distance = Math.sqrt( Math.pow(locations[i]['latitude']-user_coords[0], 2) + Math.pow(locations[i]['longitude']-user_coords[1], 2));

        // If this distance is less than the last distance, or there is no last distance
        if (nearest_distance == -1 || current_distance < nearest_distance) {
          nearest = [locations[i]['latitude'], locations[i]['longitude']];
          nearest_distance = current_distance;
        }

      }

      if (nearest) {
        return nearest;
      } else {
        return false;
      }

    }

  });

});
