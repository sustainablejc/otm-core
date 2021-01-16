import React from 'react';
import { useLeafletContext, LayerProps,
  createTileLayerComponent,
  updateGridLayer,
  withPane } from '@react-leaflet/core';
import L from 'leaflet';
import '../L.UTFGrid-min';

/*
export class UtfGrid extends Layer {


	addEvents() { 
		if (this.props.mouseMove) {
			this.leafletElement.on('mousemove', this.props.mouseMove);
		};

		if (this.props.mouseOver) {
			this.leafletElement.on('mouseover', this.props.mouseOver);
		};

		if (this.props.mouseOut) {
			this.leafletElement.on('mouseout', this.props.mouseOut);
		};

		if (this.props.onClick) {
			this.leafletElement.on('click', this.props.onClick);
		};
	}

	removeEvents() {
		if (this.props.mouseMove) {
			this.leafletElement.off('mousemove', this.props.mouseMove);
		};

		if (this.props.mouseOver) {
			this.leafletElement.off('mouseover', this.props.mouseOver);
		};

		if (this.props.mouseOut) {
			this.leafletElement.off('mouseout', this.props.mouseOut);
		};

		if (this.props.onClick) {
			this.leafletElement.off('click', this.props.onClick);
		};
	}

	componentWillMount() {
		this.leafletElement = new L.UtfGrid(this.props.url, this.props.options);
		this.addEvents();
	}

	componentWillUnmount() {
		this.removeEvents();
	}	

	createLeafletElement() {
		return this.leafletElement;
	}
}

export default withLeaflet(UtfGrid);
*/

export const UtfGrid = createTileLayerComponent(
    function createTileLayer({ url, ...options }, context) {
        const layer = new L.UTFGrid(url, options);

        layer.setUrl = function(url) {
            layer._url = url;
            layer._cache = {};
            layer._update();
        }

        layer.on('click', function(event) {
            if (event.id == null) return;
            //L.popup().setLatLng([event.latlng.lat, event.latlng.lng]).openOn(context.map);
        });

		//this.leafletElement = new L.UtfGrid(this.props.url, this.props.options);
        return {
            //instance: new LeafletTileLayer(url, withPane(options, context)),
            instance: layer,
            context,
        }
    },
    updateGridLayer);


export const MyComponent = (props) => {
  const context = useLeafletContext();

  React.useEffect(() => {
    const container = context.layerContainer || context.map;
    const layer = new L.utfGrid(props.url, props.options);

    layer.setUrl = function(url) {
        layer._url = url;
        layer._cache = {};
        layer._update();
    }

    container.addLayer(layer);

    return () => {
      debugger;
      container.removeLayer(layer);
    };
  });

  return null;
};

export default UtfGrid;
