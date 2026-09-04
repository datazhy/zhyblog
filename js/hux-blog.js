/*!
 * Clean Blog v1.0.0 (http://startbootstrap.com)
 * Copyright 2015 Start Bootstrap
 * Licensed under Apache 2.0 (https://github.com/IronSummitMedia/startbootstrap/blob/gh-pages/LICENSE)
 */

 /*!
 * Hux Blog v1.6.0 (http://startbootstrap.com)
 * Copyright 2016 @huxpro
 * Licensed under Apache 2.0 
 */

// Light / dark / system theme toggle
(function () {
    var key = 'zhy-theme';
    var modes = ['auto', 'light', 'dark'];
    var isEnglish = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0;
    var labels = isEnglish
        ? { auto: 'Auto', light: 'Light', dark: 'Dark' }
        : { auto: '自动', light: '亮色', dark: '暗色' };
    var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

    function currentTheme() {
        var value = document.documentElement.getAttribute('data-theme');
        return modes.indexOf(value) > -1 ? value : 'auto';
    }

    function isDark(theme) {
        return theme === 'dark' || (theme === 'auto' && media && media.matches);
    }

    function applyTheme(theme, persist) {
        var dark = isDark(theme);
        var root = document.documentElement;
        var button = document.getElementById('theme-toggle');
        var meta = document.querySelector('meta[name="theme-color"]');

        root.setAttribute('data-theme', theme);
        root.style.colorScheme = dark ? 'dark' : 'light';
        if (meta) meta.setAttribute('content', dark ? '#11161d' : '#ffffff');

        if (button) {
            var text = isEnglish
                ? 'Theme: ' + labels[theme] + ' (click to switch)'
                : '主题：' + labels[theme] + '（点击切换）';
            button.setAttribute('aria-label', text);
            button.setAttribute('title', text);
            var label = button.querySelector('.theme-toggle-label');
            if (label) label.textContent = labels[theme];
        }

        if (persist) {
            try { localStorage.setItem(key, theme); } catch (e) {}
        }
    }

    function initThemeToggle() {
        var button = document.getElementById('theme-toggle');
        applyTheme(currentTheme(), false);
        if (!button) return;

        button.addEventListener('click', function () {
            var theme = currentTheme();
            applyTheme(modes[(modes.indexOf(theme) + 1) % modes.length], true);
        });
    }

    if (media) {
        var onSystemThemeChange = function () {
            if (currentTheme() === 'auto') applyTheme('auto', false);
        };
        if (media.addEventListener) media.addEventListener('change', onSystemThemeChange);
        else if (media.addListener) media.addListener(onSystemThemeChange);
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initThemeToggle);
    else initThemeToggle();
})();

// Tooltip Init
// Unuse by Hux since V1.6: Titles now display by default so there is no need for tooltip
// $(function() {
//     $("[data-toggle='tooltip']").tooltip();
// });


// make all images responsive
/* 
 * Unuse by Hux
 * actually only Portfolio-Pages can't use it and only post-img need it.
 * so I modify the _layout/post and CSS to make post-img responsive!
 */
// $(function() {
//  $("img").addClass("img-responsive");
// });

// responsive tables
$(document).ready(function() {
    $("table").wrap("<div class='table-responsive'></div>");
    $("table").addClass("table");
});

// responsive embed videos
$(document).ready(function() {
    $('iframe[src*="youtube.com"]').wrap('<div class="embed-responsive embed-responsive-16by9"></div>');
    $('iframe[src*="youtube.com"]').addClass('embed-responsive-item');
    $('iframe[src*="vimeo.com"]').wrap('<div class="embed-responsive embed-responsive-16by9"></div>');
    $('iframe[src*="vimeo.com"]').addClass('embed-responsive-item');
});

// Navigation Scripts to Show Header on Scroll-Up
jQuery(document).ready(function($) {
    var MQL = 1170;

    //primary navigation slide-in effect
    if ($(window).width() > MQL) {
        var headerHeight = $('.navbar-custom').height(),
            bannerHeight  = $('.intro-header .container').height();     
        $(window).on('scroll', {
                previousTop: 0
            },
            function() {
                var currentTop = $(window).scrollTop(),
                    $catalog = $('.side-catalog');

                //check if user is scrolling up by mouse or keyborad
                if (currentTop < this.previousTop) {
                    //if scrolling up...
                    if (currentTop > 0 && $('.navbar-custom').hasClass('is-fixed')) {
                        $('.navbar-custom').addClass('is-visible');
                    } else {
                        $('.navbar-custom').removeClass('is-visible is-fixed');
                    }
                } else {
                    //if scrolling down...
                    $('.navbar-custom').removeClass('is-visible');
                    if (currentTop > headerHeight && !$('.navbar-custom').hasClass('is-fixed')) $('.navbar-custom').addClass('is-fixed');
                }
                this.previousTop = currentTop;


                //adjust the appearance of side-catalog
                $catalog.show()
                if (currentTop > (bannerHeight + 41)) {
                    $catalog.addClass('fixed')
                } else {
                    $catalog.removeClass('fixed')
                }
            });
    }
});