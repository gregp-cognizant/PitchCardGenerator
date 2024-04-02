import React, { useState, useEffect } from 'react';
import '../css/SpinnerWithTimer.css';

function SpinnerWithTimer() {
    const [seconds, setSeconds] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setSeconds(seconds => seconds + 1);
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    return (
        // Align the spinner and timer in the middle of the screen
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
            <div className="spinner"></div>
            <div style={{ marginLeft: '10px' }}>
                {seconds} seconds
            </div>
        </div>
    );
}

export default SpinnerWithTimer;
