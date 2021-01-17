import React, { Component } from 'react';
import L from 'leaflet';
import { Container, Col, Row } from 'react-bootstrap';
import { LayersControl, MapContainer, TileLayer, Marker, Overlay, Popup } from "react-leaflet";
import ReactLeafletGoogleLayer from 'react-leaflet-google-layer';
import { createSignature } from '../common/util/ApiRequest';
import axios from 'axios';
import config from 'treemap/lib/config';
import { PlotTileLayer } from './Layers';
import { PlotUtfTileLayer } from './Layers';
import { TreePopup } from './TreePopup';

import 'leaflet/dist/leaflet.css';
import './Map.css';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// the below is a bugfix found in the following
// https://stackoverflow.com/questions/49441600/react-leaflet-marker-files-not-found
// https://github.com/Leaflet/Leaflet/issues/4968
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;

const key = '';


export default class Map extends Component {
    constructor(props) {
        super(props);
        this.state = {
            startingLatitude: null,
            startingLongitude: null,
            loading: true,
            popupInfo: {
                ids: null,
                show: false,
                latLng: { lat: null, lng: null }
            }
        }
    }

    componentDidMount() {

        var url = 'http://localhost:8080/api/v2/instance/JerseyCity';
        createSignature(url)
            .then(x => {
                this.setState({
                    startingLongitude: x['data']['center']['lng'],
                    startingLatitude: x['data']['center']['lat'],
                    loading: false
                });
            }).catch(x => {
                console.log('Error fetching map');
                console.log(x);
            });

        axios.get('/jerseycity/species/', {withCredential: true})
            .then(x => {
                //debugger;
            }).catch(x => {
                //debugger;
            });
    }

    render() {
        const {loading, startingLongitude, startingLatitude, popupInfo} = this.state;

        const utfEventHandlers = {
            click: (event) => {
                if (event.id == null) {
                    this.setState({
                        popupInfo: {
                            ids: null,
                            show: false,
                            latLng: { lat: null, lng: null }
                        }
                    });
                } else {
                    this.setState({
                        popupInfo: {
                            // FIXME can there be multiple?
                            ids: [event.id],
                            show: true,
                            latLng: { lat: event.latlng.lat, lng: event.latlng.lng }
                        }
                    });
                }
            }
        }
        const popup = popupInfo.show ? (
            <TreePopup {...popupInfo} />
        ) : null;

        if (loading) return (<div>Loading...</div>);

        return (
        <div>
            <MapContainer center={[startingLongitude, startingLatitude]} zoom={13} scrollWheelZoom={true}>
                <LayersControl position='topright'>
                    <LayersControl.BaseLayer checked name='OpenStreetMap'>
                        <TileLayer
                            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>
                    <LayersControl.BaseLayer name='OpenStreetMap2'>
                        <TileLayer
                            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>
                    <LayersControl.BaseLayer name='Google Hybrid'>
                        <ReactLeafletGoogleLayer
                            apiKey={key}
                            type={'satellite'}
                        />
                    </LayersControl.BaseLayer>
                    <LayersControl.BaseLayer name='Google Streets'>
                        <ReactLeafletGoogleLayer
                            apiKey={key}
                            type={'roadmap'}
                        />
                    </LayersControl.BaseLayer>
                </LayersControl>
                <PlotTileLayer />
                <PlotUtfTileLayer eventHandlers={utfEventHandlers} />
                {popup}
            </MapContainer>
        </div>
        );
    }
}
