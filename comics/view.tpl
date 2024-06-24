% include('header.tpl', title="View Comic")
<script>
$( document ).ready(function() {
    const container = document.getElementById("gallery-container");
    lightGallery(container, {
        speed: 500,
        plugins: [lgZoom, lgFullscreen]
    });

    const requestFullScreen = () => {
        const el = document.documentElement;
        if (el.requestFullscreen) {
            el.requestFullscreen();
        } else if (el.msRequestFullscreen) {
            el.msRequestFullscreen();
        } else if (el.mozRequestFullScreen) {
            el.mozRequestFullScreen();
        } else if (el.webkitRequestFullscreen) {
            el.webkitRequestFullscreen();
        }
    };
    container.addEventListener("lgAfterOpen", () => {
        requestFullScreen();
    });
});
</script>

<div class="header d-flex flex-column align-items-center">
  <h1 class="display-6 mt-3 mb-0">lightGallery</h1>
  <p class="lead mt-2 mb-4">
    lightGallery is a feature-rich, modular JavaScript gallery plugin for building beautiful image and video galleries for the web and the mobile
  </p>
  <a class="btn mb-5 btn-outline-primary" href="https://github.com/sachinchoolur/lightGallery" target="_blank">View on GitHub</a>
</div>
<div class="gallery-container d-flex align-items-center justify-content-center" id="gallery-container">
% for i, filename in enumerate(files):
% if i:
    <a class="gallery-item" data-src="{{filename}}"></a>
% else:
    <a class="gallery-item" data-src="{{filename}}"><img src="{{thumb}}"></a>
% end
% end
<!--
  <a data-lg-size="1400-1400" class="gallery-item" data-src="https://images.unsplash.com/photo-1588093413519-17cec3f64e40?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=1400&q=80" data-sub-html="<h4>Photo by - <a href='https://unsplash.com/@entrycube' >Diego Guzmán </a></h4> <p> Location - <a href='https://unsplash.com/s/photos/fushimi-inari-taisha-shrine-senbontorii%2C-68%E7%95%AA%E5%9C%B0-fukakusa-yabunouchicho%2C-fushimi-ward%2C-kyoto%2C-japan'>Fushimi Ward, Kyoto, Japan</a></p>">
    <img class="img-fluid" src="https://images.unsplash.com/photo-1588093413519-17cec3f64e40?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=240&q=80" />
  </a>
  <a data-lg-size="1443-1329" class="gallery-item" data-src="https://images.unsplash.com/photo-1563502310703-1ffe473ad66d?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=1443&q=80" data-sub-html="<h4>Photo by - <a href='https://unsplash.com/@asoshiation' >Shah </a></h4><p> Location - <a href='https://unsplash.com/s/photos/shinimamiya%2C-osaka%2C-japan'>Shinimamiya, Osaka, Japan</a></p>">
    <img class="img-fluid" src="https://images.unsplash.com/photo-1563502310703-1ffe473ad66d?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=240&q=80" />
  </a>
  <a data-lg-size="1400-1402" class="gallery-item" data-src="https://images.unsplash.com/photo-1613541444699-39429d990353?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=1400&q=80" data-sub-html="<h4>Photo by - <a href='https://unsplash.com/@katherine_xx11' >Katherine Gu </a></h4><p> For all those years we were alone and helpless.</p>">
    <img class="img-fluid" src="https://images.unsplash.com/photo-1613541444699-39429d990353?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=240&q=80" />
  </a>
-->
</div>
<script src="/static/js/lightgallery.umd.js"></script>
<script src="/static/js/lg-fullscreen.umd.js"></script>
<script src="/static/js/lg-zoom.umd.js"></script>

% include('footer.tpl')
