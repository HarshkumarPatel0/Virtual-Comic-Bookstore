% include('header.tpl', title="Add Scans")
<div class="row">
    <div class="col">
        <form action="/add" method="post">
            <input name="action" type="hidden" value="{{action}}">
            <button name="update" type="submit" class="btn btn-primary"><i class="bi bi-folder-plus"></i> Add Scans</button>
        </form>
    </div>
</div>
% include('footer.tpl')
