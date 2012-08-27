<?php
set_time_limit(0);
require_once './class/simple_html_dom.php';

$url = "http://www.nhi.gov.tw/query/query1_list.aspx";
$agent = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5';

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, TRUE);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE); 
curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data); 
curl_setopt($ch, CURLOPT_HTTPHEADER, array("User-Agent:" . $agent));
$response_html = curl_exec($ch);
curl_close($ch);

$html = str_get_html($response_html);
$input_viewstate = $html->find('input[id=__VIEWSTATE]', 0)->value;
$input_eventvalidation = $html->find('input[id=__EVENTVALIDATION]', 0)->value;

$html->clear();
unset($html);

$post_data = array();
$post_data["__EVENTTARGET"] = "ddlPageSelect";
$post_data["ddlPageSelect"] = 1; 
$post_data["hiddenPage"] = $post_data["ddlPageSelect"] - 1;
$post_data["__VIEWSTATE"] = $input_viewstate;
$post_data["__EVENTVALIDATION"] = $input_eventvalidation;
$post_data["hiddenPageNum"] = 10;

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, TRUE);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE); 
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($post_data)); 
curl_setopt($ch, CURLOPT_HTTPHEADER, array("User-Agent:" . $agent));
$response_html = curl_exec($ch);
curl_close($ch);

echo $response_html;

/*
$html = str_get_html($response_html);
$dom = $html->find('.GridView', 0);

echo $dom;

$html->clear();
 */
exit();
?>
