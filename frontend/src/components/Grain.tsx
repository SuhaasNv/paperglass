/** The paper grain: one SVG filter, one fixed overlay, multiplied at 32 percent. */
export function Grain() {
  return (
    <>
      <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
          <feComponentTransfer>
            <feFuncA type="table" tableValues="0 0 0 .18" />
          </feComponentTransfer>
        </filter>
      </svg>
      <div className="grain" aria-hidden="true" />
    </>
  )
}
