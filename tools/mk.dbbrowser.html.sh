

# https://developer.mozilla.org/en-US/docs/Web/CSS/Layout_cookbook/Sticky_footers

cat <<-EOE > ../html/dbbrowser.html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- <meta name="application-name" content=""> -->

    <title></title>

    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <link rel="stylesheet" href="styles.css">
<style>

EOE

cat ../clients/JavaScript/css/db-api.css >> ../html/dbbrowser.html

cat <<-EOE >> ../html/dbbrowser.html

</style>
</head>
<body>
    <noscript>Please Enable JavaScript</noscript>
    <section>
        <div class="wrapper">
            <header class="page-header"></header>
            <main class="page-body">
                <div class="container"></div>
            </main>
            <footer class="page-footer"></footer>
        </div>
    </section>
<script type="text/javascript" defer="defer">
EOE

cat ../clients/JavaScript/js/db-api.js >> ../html/dbbrowser.html

cat <<-EOE >> ../html/dbbrowser.html

</script>
</body>
</html>
EOE



