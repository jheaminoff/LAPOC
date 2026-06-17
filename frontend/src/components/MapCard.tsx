/**
 * MapCard — parses MAP: tool output text and renders a Leaflet map with a marker.
 *
 * Expected input format (from agent/tools.py lookup_address):
 *   MAP:
 *     latitude: 34.0490609096
 *     longitude: -118.325872923
 */

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import styles from './MapCard.module.css'

// ─── Fix Leaflet default marker icon for bundlers ─────────────────────────
// The default icon uses hardcoded paths that break under Vite/webpack.
// This replaces them with stable CDN URLs.

const defaultIcon = L.icon({
  iconRetinaUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})
L.Marker.prototype.options.icon = defaultIcon

// ─── Types ─────────────────────────────────────────────────────────────────

interface MapData {
  latitude: number
  longitude: number
}

// ─── Parser ────────────────────────────────────────────────────────────────

/**
 * Parse raw MAP: tool text into a MapData object.
 * Returns null if the text doesn't contain a valid MAP: block.
 */
export function parseMapText(text: string): MapData | null {
  if (!text.includes('MAP:')) return null

  const lines = text.split('\n')
  const mapIdx = lines.findIndex((l) => l.trim().startsWith('MAP:'))
  if (mapIdx === -1) return null

  const extract = (label: string): string => {
    const line = lines.find((l) => l.trimStart().startsWith(label))
    return line ? line.slice(line.indexOf(label) + label.length).trim() : ''
  }

  const latStr = extract('latitude:')
  const lngStr = extract('longitude:')
  const latitude = parseFloat(latStr)
  const longitude = parseFloat(lngStr)

  if (isNaN(latitude) || isNaN(longitude)) return null
  return { latitude, longitude }
}

// ─── Main component ────────────────────────────────────────────────────────

interface Props {
  data: MapData
}

export default function MapCard({ data }: Props) {
  const position: [number, number] = [data.latitude, data.longitude]

  return (
    <div className={styles.card}>
      <MapContainer
        center={position}
        zoom={16}
        scrollWheelZoom={false}
        className={styles.map}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={position}>
          <Popup>
            {data.latitude.toFixed(6)}, {data.longitude.toFixed(6)}
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
