import React, { useEffect, useRef } from 'react';

const MolstarViewer = ({ xyzData }) => {
  const viewerRef = useRef(null);

  useEffect(() => {
    // This is a placeholder for Molstar initialization.
    // In a real setup, we would load the molstar plugin and attach it to viewerRef.current
    if (viewerRef.current) {
        viewerRef.current.innerHTML = "<div style='display:flex; height:100%; align-items:center; justify-content:center; color:#94a3b8;'>Molstar Viewer Instance Loading...<br/>Data:<br/><pre>" + xyzData + "</pre></div>";
    }
  }, [xyzData]);

  return <div ref={viewerRef} className="w-full h-full" />;
};

export default MolstarViewer;
