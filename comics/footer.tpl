% if selection:
<div class="row">
<div class="col">
<button onclick="window.location.href='{{path}}?page={{page-1}}';" type="button" class="btn btn-primary btn-lg"><i class="bi bi-arrow-bar-left"></i> Previous</button>
<button onclick="window.location.href='{{path}}?page={{page+1}}';" type="button" class="btn btn-primary btn-lg float-right">Next <i class="bi bi-arrow-bar-right"></i></button>
</div>
</div>
% end

</div> <!--container-->
<footer>&copy; 2022 Harsh Patel</footer>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="/static/js/bootstrap.min.js"></script>
<script>
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
</script>

</body>
</html>