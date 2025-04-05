if(!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    update_width: function(n_intervals) {
        return window.innerWidth;
    },
    detect_mobile: function(trigger) {
        // Initial check
        let checkMobile = function() {
            return window.innerWidth < 768 ? 'mobile' : 'desktop';
        };
        
        // Add resize listener if not already added
        if (!window.mobileViewListener) {
            window.mobileViewListener = true;
            window.addEventListener('resize', function() {
                // Trigger a click on the viewport container to force callback
                document.getElementById('viewport-container').click();
            });
        }
        
        return checkMobile();
    }
}; 