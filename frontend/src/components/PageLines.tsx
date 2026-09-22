/** Printed lines standing in for a page's body where there is no raster to show. */
export function PageLines({ scale = 1 }: { scale?: number }) {
  const spec: Array<[number, number]> = [[0.22, 0.9], [0.86, 0.55], [0.78, 0.55], [0.64, 0.55], [0, 0], [0.18, 0.9], [0.7, 0.55], [0.52, 0.55]]
  return (
    <div aria-hidden="true">
      {spec.map(([w, o], i) =>
        w === 0 ? (
          <div key={i} style={{ height: Math.round(40 * scale) }} />
        ) : (
          <div
            key={i}
            className="doc-line"
            style={{ width: `${Math.round(w * 100)}%`, opacity: o, height: Math.max(4, Math.round(7 * scale)), margin: `${Math.max(4, Math.round(8 * scale))}px 0` }}
          />
        ),
      )}
    </div>
  )
}
