import _ from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import config from 'treemap/lib/config';
import { TileLayer, Marker, Popup } from "react-leaflet";
import TreePopup from './TreePopup';
import UtfGrid from './UtfGrid';


export function PlotTileLayer(props) {
    const MAX_ZOOM_OPTION = {maxZoom: 21};
    // Min zoom level for detail layers
    const MIN_ZOOM_OPTION = {minZoom: 15};

    const FEATURE_LAYER_OPTION = {zIndex: 4};

    const ref = useRef();
    const options = _.extend({}, MAX_ZOOM_OPTION, FEATURE_LAYER_OPTION);
    useEffect(() => {
        var t = ref;
    });
    const noSearchUrl = filterableLayer('treemap_mapfeature', 'png', options, {});

    return <TileLayer url={noSearchUrl} {...options} />;
}


export function PlotUtfTileLayer(props) {
    const MAX_ZOOM_OPTION = {maxZoom: 21};
    // Min zoom level for detail layers
    const MIN_ZOOM_OPTION = {minZoom: 15};
    const [showMarker, setShowMarker] = useState(false);
    const [latLng, setLatLng] = useState({ lat: null, lng: null});

    const FEATURE_LAYER_OPTION = {zIndex: 4};

    const options = _.extend({resolution: 4}, MAX_ZOOM_OPTION, FEATURE_LAYER_OPTION);
    const url = getUrlMaker('treemap_mapfeature', 'grid.json')();

    //return (<UtfGrid url={url} eventHandlers={eventHandlers} {...options}>
    return (<UtfGrid url={url} eventHandlers={props.eventHandlers} {...options} />);
}


function filterableLayer (table, extension, layerOptions, tilerArgs) {
    var revToUrl = getUrlMaker(table, extension, tilerArgs),
        noSearchUrl = revToUrl(config.instance.geoRevHash),
        searchBaseUrl = revToUrl(config.instance.universalRevHash);
        //layer = L.tileLayer(noSearchUrl, layerOptions);

    /*
    layer.setHashes = function(response) {
        noSearchUrl = revToUrl(response.geoRevHash);
        searchBaseUrl = revToUrl(response.universalRevHash);

        // Update tiles to reflect content changes.
        var newLayerUrl = updateBaseUrl(layer._url, searchBaseUrl);
        layer.setUrl(newLayerUrl);
    };

    layer.setFilter = function(filters) {
        var fullUrl;
        if (Search.isEmpty(filters)) {
            fullUrl = noSearchUrl;
        } else {
            var query = Search.makeQueryStringFromFilters(filters);
            var suffix = query ? '&' + query : '';
            fullUrl = searchBaseUrl + suffix;
        }
        layer.setUrl(fullUrl);
    };
    */

    //return (<TileLayer url={noSearchUrl} />);
    return noSearchUrl;
}


function getUrlMaker(table, extension, tilerArgs) {
    return function revToUrl(rev) {
        var query = {
            'instance_id': config.instance.id,
            'restrict': JSON.stringify(config.instance.mapFeatureTypes)
        };

        if (tilerArgs) {
            _.extend(query, tilerArgs);
        }

        var paramString = new URLSearchParams(query).toString();
        return `${config.tileHost || ''}/tile/${rev}/database/otm/table/${table}/`
            + `{z}/{x}/{y}.${extension}?${paramString}`;
    };
}
