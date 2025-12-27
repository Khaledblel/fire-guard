document.addEventListener('DOMContentLoaded', () => {
    const sliders = document.querySelectorAll('.sync-range');
    
    sliders.forEach(slider => {
        const targetId = slider.getAttribute('data-target');
        const numberInput = document.getElementById(targetId);
        const colorType = slider.getAttribute('data-color-type');

        // Initial color set
        updateColor(slider, colorType);

        // Event: Slider bouge -> change Number
        slider.addEventListener('input', (e) => {
            numberInput.value = e.target.value;
            updateColor(e.target, colorType);
        });

        // Event: Number change -> bouge Slider
        numberInput.addEventListener('input', (e) => {
            let val = parseFloat(e.target.value);
            const min = parseFloat(slider.min);
            const max = parseFloat(slider.max);

            // Validation simple pour éviter que le thumb disparaisse
            if (val > max) val = max; 
            if (val < min) val = min;
            
            slider.value = val;
            updateColor(slider, colorType);
        });
    });
});

// Fonction magique pour changer la couleur du bouton rond (Thumb)
function updateColor(sliderElement, type) {
    const val = parseFloat(sliderElement.value);
    const min = parseFloat(sliderElement.min);
    const max = parseFloat(sliderElement.max);
    
    // Calcul du pourcentage entre 0 et 1
    let percent = (val - min) / (max - min); 
    // Protection division par zéro ou NaN
    if (isNaN(percent)) percent = 0.5;

    let color = "#fff";

    if (type === 'temp') {
        // Bleu vers Rouge
        color = interpolateColor('#3b82f6', '#ef4444', percent);
    } 
    else if (type === 'humidity') {
        // Rouge (Sec=Danger) vers Bleu (Humide=Sûr)
        // Note : Basse humidité = danger feu
        color = interpolateColor('#ef4444', '#3b82f6', percent);
    } 
    else if (type === 'wind') {
        // Vert (Calme) vers Rouge (Danger)
        color = interpolateColor('#10b981', '#ef4444', percent);
    } 
    else if (type === 'rain') {
        // Orange (Sec) vers Bleu (Pluie)
        color = interpolateColor('#f97316', '#3b82f6', percent);
    }

    // Applique la variable CSS locale
    sliderElement.style.setProperty('--thumb-color', color);
}

// Helper pour mixer deux couleurs hexadécimales
function interpolateColor(color1, color2, factor) {
    if (arguments.length < 3) { factor = 0.5; }
    
    var r1 = parseInt(color1.substring(1, 3), 16);
    var g1 = parseInt(color1.substring(3, 5), 16);
    var b1 = parseInt(color1.substring(5, 7), 16);

    var r2 = parseInt(color2.substring(1, 3), 16);
    var g2 = parseInt(color2.substring(3, 5), 16);
    var b2 = parseInt(color2.substring(5, 7), 16);

    var r = Math.round(r1 + factor * (r2 - r1));
    var g = Math.round(g1 + factor * (g2 - g1));
    var b = Math.round(b1 + factor * (b2 - b1));

    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}