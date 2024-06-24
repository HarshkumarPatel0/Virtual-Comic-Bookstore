% include('header.tpl', title="Comics")
% if extract:
<h2>Extracting {{extract.notes}}</h2>
    <script>
    $( document ).ready(function() {
        $.ajax({
            url: "extract/{{extract.id}}",
            context: document.body
        }).done(function() {
            location.reload(true);
        });
    });
    </script>
% end

% if form_title:
<div class="form">

    <div>
      <h1>{{form_title}} Comic {{instance}}</h1>

      <form action="/comic" method="post">

      <input name="action" type="hidden" value="{{action}}">
% if instance:
      <input name="id" type="hidden" value="{{instance.id}}">
% end

      <div class="full-row">
        <div class="field-wrap">
          <label class="active">
            Genre<span class="req">*</span>
          </label>
            <select name="genre">
% for curr in genres:
                {!curr.option(instance and instance.genre)}
% end
            </select>
        </div>
      </div>

      <div class="full-row">
        <div class="field-wrap">
          <label>
              Title<span class="req">*</span>
          </label>
            <input name="title" type="text" {{required}} autocomplete="off" value="{{instance and instance.title}}"/>
        </div>
      </div>

      <div class="full-row">
        <div class="field-wrap">
          <label>
            Notes
          </label>
            <input name="notes" type="text" autocomplete="off" value="{{instance and instance.notes}}"/>
        </div>
      </div>

      <button name="update" type="submit" class="button button-block"/>{{form_submit}}</button>
% if instance:
      <br/>
    <button name="delete" type="submit" class="button button-block"/>Delete</button>
% end

      </form>

    </div>


</div> <!-- /form -->

% else:
<div class="row">
<div class="col">
<h2><a href="/comic/search">Search</a></h2>
</div>
</div>
<div class="row">
<div class="col">
<table border="1" class="table table-striped">
    <tr><th width="20%">Series</th><th>Issue</th><th>Date</th><th>Notes</th><th>Cover</th></tr>
% for comic in objects:
    <tr class=""><td>{{comic.series_name}}</td><td>{{comic.issue}}</td><td>{{comic.display_date}}</td><td>{{!comic.html_notes}}</td><td>{{!comic.thumb}}</td></tr>
% end
</table>
% end
</div>
</div>
% include('footer.tpl')
