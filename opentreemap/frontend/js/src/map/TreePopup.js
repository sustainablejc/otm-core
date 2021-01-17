import React, { useEffect, useRef, useState } from 'react';
import { TileLayer, Marker, Popup } from "react-leaflet";
import axios from 'axios';


export function TreePopup(props) {
    const { latLng, ids } = props;
    const [title, setTitle] = useState(null);
    const [canEdit, setCanEdit] = useState(false);
    const instance_url = window.django.instance_url;

    useEffect(() => {
        // clear the title before loading a new one
        var url = `/${instance_url}/features/${ids[0]}/popup_detail`;
        setTitle(null);
        setCanEdit(false);
        axios.get(url, {withCredential: true})
            .then(res => {
                const feature = res.data.features[0];
                setTitle(res.data.features[0].title);
                setCanEdit(window.django.user.is_authenticated
                    && feature.is_plot
                    && feature.is_editable);
            }).catch(res => {
                setTitle(null);
                setCanEdit(false);
            });
    }, [ids]);

    if (title == null) {
        return (
            <Popup position={latLng}>
                Loading...
            </Popup>
        );
    }

    return (
        <Popup position={latLng}>
            <div id="map-feature-content">
                <div className="popup-content">
                    <h4>{title}</h4>
                    <div className="popup-btns">
                        <a href={`/${window.django.instance_url}/features/${ids[0]}`} className="btn btn-sm btn-secondary">More Details</a>
                        { canEdit
                            ? <a href={`/${window.django.instance_url}/features/${ids[0]}/edit`} className="btn btn-sm btn-info">Edit</a>
                            : ""
                        }
                    </div>
                </div>
            </div>
        </Popup>
    );
}
