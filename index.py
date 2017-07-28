import datetime
import re
import psycopg2
import psycopg2.extras
from bottle import route, request, get, post, response
from math import ceil


CONN_STRING = 'host=127.0.0.1 dbname=tasti user=tasti password="" port=5432'

def get_index():
    """Returns main page/index content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="{h}css/main.css" />
</head>
<body><div id="wrapper">
        <div id="header">'''.format(h=base_url)
    return_data += top
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += do_bmarks()
    return_data += '''<div class="clear"></div>
        </div>
        <div id="rightcolumn">
                '''
    return_data += list_tags()
    return_data += '''<div class="clear"></div>
        </div>
    </div>
    <div id="footer">'''
    return_data += footer()

    bottom = '''</div>
    </div>
</body>
</html>
    '''
    return_data += bottom
    return return_data


def header0():
    """Header content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    auth_payload = auth_check()
    if auth_payload['is_authenticated']:
        header_string = '''&nbsp;Hi <A HREF="{h}account">{u}</a>&nbsp;|&nbsp;<A HREF="{h}login?do=1">Logout</a><BR><BR>
                           <UL><LI><A HREF="{h}add">ADD</a>&nbsp;a&nbsp;bookmark<LI>
                           <A HREF="{h}bmarks?whose=mine">MY BOOKMARKS</a></UL>'''.format(h=base_url,
                                                                                          u=auth_payload['username'])
    else:
        header_string = '''&nbsp;<A HREF="{h}login?do=0">Login</a>
                           &nbsp;|&nbsp;<A HREF="{h}register">Register</a>&nbsp;'''.format(h=base_url)
    return_data = '''<span class="header_class1"><TABLE width="100%"><TR>
    <TD><A HREF="{h}"><IMG SRC="{h}images/tasti-logo.png"></a></TD>
    <TD>&nbsp;</TD><TD align="right" valign="top">{header}</TD>
    </TR></TABLE></span>'''.format(header=header_string,
                                   h=base_url)
    return return_data


def do_tags():
    """Show bookmarks associated with a tag."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    user_num_bmarks = 15
    num_bmarks_menu_offset = 53
    return_data = ''
    tag_id = ''
    tag_get = ''
    show_mine = ''
    auth = auth_check()
    if request.query.get('id'):
        tag_id = request.query.get('id')
        tag_get = '&id={}'.format(tag_id)
    tags_sql = 'SELECT tag FROM tags '
    if hash_check():
        username = request.get_cookie('tasti_username').lower()
        if request.query.get('mine') and request.query.get('mine') == 'yes':
            show_mine = "AND owner='{}'".format(username)
            num_bmarks_menu_offset = 60
        if tag_id:
            tags_sql += "WHERE id='{t}' {m} LIMIT 1".format(t=tag_id,
                                                            m=show_mine)
        else:
            tags_sql += 'WHERE true=true {m} ORDER BY id DESC LIMIT 1'.format(m=show_mine)
    else:
        username = ''
        if tag_id:
            tags_sql += "WHERE id='{t}' LIMIT 1".format(t=tag_id)
        else:
            tags_sql += 'ORDER BY id DESC LIMIT 1'
    tags_qry = db_qry([tags_sql, None], 'select')
    if not tags_qry:
        return_data += '<span class="bad">Tags query FAILED:<BR>{}<BR>'.format(tags_sql)
        return return_data
    tag_count = len(tags_qry)
    if tag_count:
        tags = [t[0] for t in tags_qry]
        if request.get_cookie('tasti_bmarks_per_page'):
            bmarks_per_page = request.get_cookie('tasti_bmarks_per_page')
        if request.query.get('num') and re.match('\d', request.query.get('num')):
            user_num_bmarks = request.query.get('num')
            # 190 days until expiration
            cookie_expire = datetime.datetime.now() + datetime.timedelta(days=190)
            response.set_cookie('tasti_bmarks_per_page', user_num_bmarks, expires=cookie_expire)   
        limit_sql = ' LIMIT {}'.format(user_num_bmarks)
        marker_dict = get_markers(user_num_bmarks)  
        # pagination setup
        page = 1
        if request.query.get('page'):
            page = int(request.query.get('page'))
        prev = int(page) - 1
        next = int(page) + 1
        max_results = user_num_bmarks
        # Calculate the offset
        from_offset = (int(page) * int(max_results)) - int(max_results)
        url_get_base = '{h}{u}'.format(h=base_url,
                                       u=request.environ.get('QUERY_STRING'))
        tag = tags[0]
        bmarks_sql_base = "SELECT id, date(last_update) as last_update, owner, url, notes, name FROM bmarks WHERE tag='{t}' ".format(t=tag)
        if username and request.query.get('mine') and request.query.get('mine') == 'yes':
            bmarks_sql_base += " AND owner='{u}' ".format(u=username)
            mine = '&mine=yes'
        else:
            mine = ''
        bmarks_sql_all = '{bm} ORDER BY owner, last_update, name'.format(bm=bmarks_sql_base)
        bmarks_sql = '{bm} {l} OFFSET {o}'.format(bm=bmarks_sql_all, l=limit_sql, o=from_offset)
        bmarks_qry = db_qry([bmarks_sql, None], 'select')
        if not bmarks_qry:
            return_data += '<span class="bad">Bmarks query FAILED:<BR>{}<BR>'.format(bmarks_sql)
            return return_data
        bmarks_qry_all_res = db_qry([bmarks_sql_all, None], 'select')
        if not bmarks_qry_all_res:
            return_data += '<span class="bad">Bmarks All query FAILED:<BR>{}<BR>'.format(bmarks_sql_all)
            return return_data
        num_bmarks_all = len(bmarks_qry_all_res)
        num_bmarks = len(bmarks_qry)
        if num_bmarks:
            left_td_width = 100 - (22 + len(tag))
            return_data += '''<TABLE width="100%"><TR>
                                <TD width="{lw}%">
                                <span class="huge">Bookmarks tagged with <B>{t}</B></span></TD>'''.format(lw=left_td_width, t=tag)
            # only render the bmarks/page menu on the 'MY BOOKMARKS' page
            if hash_check():
                return_data += '''<TD valign="top"><div id="menu">
                                    <UL id="item1">
                                    <LI class="top"><B>Bookmarks/page</B></LI>
                                        <LI class="item"><A HREF="{u}num=5">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a5}5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=10">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a10}10&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=15">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a15}15&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a20}20&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=30">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a30}30&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI></UL>
                                    </DIV>&nbsp;</TD>'''.format(n=num_bmarks_menu_offset,
                                                                u=url_get_base,
                                                                a5=marker_dict['5'],
                                                                a10=marker_dict['10'],
                                                                a15=marker_dict['15'],
                                                                a20=marker_dict['20'],
                                                                a30=marker_dict['30'])
            return_data += '</TR></TABLE><HR><BR>'
            for bmark_row in bmarks_qry:
                notes_string = ''
                bm_id = bmark_row[0]
                last_update = bmark_row[1]
                owner = bmark_row[2]
                url = bmark_row[3]
                notes = bmark_row[4].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
                name = bmark_row[5].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
                if notes:
                    notes_string = '<BR><span class="small"><B>{n}</B></span>'.format(n=notes)
                if hash_check() and owner == username:
                    bmark_user_edit_string = '''<BR><A HREF="edit?id={i}&func=edit"><span class="normal"><B>EDIT</B></a>
                                                &nbsp;|&nbsp;<A HREF="{h}bmarks?id={i}&func=del"><B>DELETE</B></a>&nbsp;</span>'''.format(i=bm_id,
                                                                                                                                          h=base_url)
                else:
                    bmark_user_edit_string = '''<BR><span class="normal">Created by <A HREF="{h}bmarks?whose={o}">
                                                <B>{o}</B></a>&nbsp;</span>'''.format(o=owner,
                                                                                      h=base_url)
                return_data += '''<TABLE><TR>
                                    <TD valign="top" width="95"><span class="big">{l}&nbsp;&nbsp;&nbsp;</span></TD>
                                    <TD><span class="big"><A HREF="{u}">{n}</a></span>{no}{b}</TD>
                                </TR></TABLE><HR><BR>'''.format(l=last_update, u=url,
                                                                n=name, no=notes_string,
                                                                b=bmark_user_edit_string)
            # pagination settings
            my_row_count = num_bmarks_all
            total_pages = int(ceil(int(my_row_count) / float(max_results)))
            pagination = ''

            # Create a PREV link if one is needed
            if page > 1:
                pagination += '''<A STYLE="text-decoration:none" title="PREVIOUS PAGE" HREF="{h}tags?{m}&page={p}&num={u}{t}">
                                 <span class="huge"><H1>&larr;</H1></span></A>'''.format(m=mine,
                                                                                         p=prev,
                                                                                         u=user_num_bmarks,
                                                                                         h=base_url,
                                                                                         t=tag_get)
            # Create a NEXT link if one is needed
            if page < total_pages:
                pagination += '''<A STYLE="text-decoration:none" title="NEXT PAGE" HREF="{h}tags?{m}&page={n}&num={u}{t}">
                                 <span class="huge"><H1>&rarr;</H1></span></A>'''.format(m=mine, n=next, u=user_num_bmarks,
                                                                                         h=base_url, t=tag_get)
            else:
                # adjust the total count when on the last page since
                # it might not have user_num_bmarks items remaining
                new_max_results = (int(max_results) - ((int(page) * int(max_results)) - int(my_row_count)))
                max_results = new_max_results
            plural = ''
            if my_row_count:
                plural = 's'
            return_data += '''<TABLE width="100%"><TR COLSPAN="1"><TD>&nbsp;</TD></TR>
                            <TR><TD COLSPAN="9">&nbsp;{m} Tasti bookmark{p}</TD>
                            <TD class="page" COLSPAN="4"><B>{pa}</B></TD></TR></TABLE><BR>'''.format(m=my_row_count,
                                                                                                     p=plural,
                                                                                                     pa=pagination)
    else:
        return_data += 'No tags selected.<BR><BR><BR>'
    return return_data


def do_bmarks():
    """Bookmark content."""
    return_data = ''
    auth = auth_check()
    
    if auth['is_authenticated'] and auth['username'] and request.query.get('func') and request.query.get('id'):
    	username = auth['username']
        id = request.query.get('id')
        if request.query.get('func') == 'del':
            old_bmark_sql = "SELECT created, url, notes, name FROM bmarks WHERE id='{i}' LIMIT 1".format(i=id)
            old_bmark_res = ([old_bmark_sql, None], 'select')
            if not old_bmark_res:
            	return_data += '<span class="bad">Old Bookmark query FAILED<BR></span><BR><BR>'
                return return_data
            old_bmark = old_bmark_res[0]
            old_created = old_bmark[0]
            old_url = old_bmark[1]
            old_notes = old_bmark[2]
            old_name = old_bmark[3]
            sql_vals = [username, old_url, old_name, old_notes]
            bmark_del_sql = 'DELETE FROM bmarks WHERE owner=%s AND url=%s AND name=%s AND notes=%s'
            bmark_del_qry = db_qry([old_bmark_sql, sql_vals], 'del')
            if not bmark_del_qry:
            	# delete failed
            	return_data += '<span class="bad">Bookmark deletion FAILED<BR></span><BR><BR>'
                return return_data
            else:
            	return_data += '<span class="huge">Bookmark successfully deleted</span><BR><BR>'
    else:
    	return_data += show_bmarks()
    return return_data


def list_tags():
    """List tags.

	only the user's, if logged in,
    most recently added otherwise
    """
    return_data = ''
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    auth = auth_check()
    tags_sql_base = 'SELECT id, tag FROM tags '
    if auth['is_authenticated'] and auth['username']:
		tags_sql = "{s} WHERE owner='{u}' ORDER BY tag".format(s=tags_sql_base, u=auth['username'])
    else:
		tags_sql = "{s} ORDER BY last_update, tag LIMIT 50".format(s=tags_sql_base)
    tags_qry_res = db_qry([tags_sql, None], 'select')
    if not tags_qry_res:
    	return_data += '<span class="bad">Tags query FAILED<BR>'
        return return_data
    else:
    	if auth['username']:
            tag_string = '<span class="big"><B>Your Tags</B></span><BR><BR>'
            show_mine = '&mine=yes'
        else:
            tag_string = '<span class="big"><B>Recent Tags</B></span><BR><BR>'
            show_mine = ''
        num_tags = len(tags_qry_res)
        if num_tags:
            return_data += tag_string
            for tag_list in tags_qry_res:
            	tag_id = tag_list[0]
                tag = tag_list[1]
            	return_data += '&nbsp;&nbsp;<A HREF="{h}tags?id={i}{sh}">{t}</a>&nbsp;<BR>'.format(i=tag_id,
                                                                                                sh=show_mine,
                                                                                                t=tag,
                                                                                                h=base_url)
        return_data += '<BR>'
    return return_data


def get_markers(user_num_bmarks):
    """Get marker values."""
    marker_dict = {}
    vals = range(5, 35, 5)
    for val in vals:
        bmark_val = ''
        if val == int(user_num_bmarks):
            bmark_val = '*'
        marker_dict['{}'.format(val)] = bmark_val
    return marker_dict


def show_bmarks():
    """Show bookmarks."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    user_num_bmarks = 15
    mine = 'mine'
    whose = ''
    default_num_bmarks_menu_offset = 77
    return_data = ''
    if request.get_cookie('tasti_bmarks_per_page'):
        bmarks_per_page = request.get_cookie('tasti_bmarks_per_page')
    if request.query.get('num') and re.match('\d', request.query.get('num')):
        user_num_bmarks = request.query.get('num')
        # 190 days until expiration
        cookie_expire = datetime.datetime.now() + datetime.timedelta(days=190)
        response.set_cookie('tasti_bmarks_per_page', user_num_bmarks, expires=cookie_expire)
    limit_sql = ' LIMIT {}'.format(user_num_bmarks)
    marker_dict = get_markers(user_num_bmarks)
    # pagination setup
    page = 1
    if request.query.get('page'):
        page = int(request.query.get('page'))
    prev = int(page) - 1
    next = int(page) + 1
    max_results = user_num_bmarks
    # Calculate the offset
    from_offset = (int(page) * int(max_results)) - int(max_results)
    url_get_base = '{h}{u}'.format(h=base_url,
                                   u=request.environ.get('QUERY_STRING'))
    bmarks_sql_base = '''SELECT distinct ON (url) url, id, date(last_update) AS last_update, notes, name, owner
                        FROM bmarks'''
    if hash_check():
        username = request.get_cookie('tasti_username').lower()
    if request.query.get('whose') and request.query.get('whose') == mine and hash_check():
        whose = request.query.get('whose')
        url_get_base += '&'
        num_bmarks_menu_offset = default_num_bmarks_menu_offset
        bmarks_intro = '<span class="huge">Your bookmarks:</span><BR><BR>'
        bmarks_sql_all = '''{s} WHERE owner='{u}' ORDER BY url, last_update'''.format(s=bmarks_sql_base,
                                                                                      u=username)
    elif request.query.get('whose') and request.query.get('whose') != mine:
        whose = request.query.get('whose')
        url_get_base += '&'
        num_bmarks_menu_offset = 177
        bmarks_intro = '''<span class="huge">{o}'s&nbsp;bookmarks:</span><BR><BR>'''.format(o=whose)
        bmarks_sql_all = '''{s} WHERE owner='{u}' ORDER BY url, last_update'''.format(s=bmarks_sql_base,
                                                                                      u=whose)
    else:
        num_bmarks_menu_offset = 73
        url_get_base += '?'
        bmarks_intro = '<span class="huge">Recent bookmarks:</span><BR><BR>'
        bmarks_sql_all = '{s} ORDER BY url, last_update'.format(s=bmarks_sql_base)
    bmarks_sql = '{s} {l} OFFSET {o}'.format(s=bmarks_sql_all,
                                             l=limit_sql,
                                             o=from_offset)
    bmarks_qry = db_qry([bmarks_sql, None], 'select')
    if not bmarks_qry:
        return_data += '<span class="bad">Bmarks query FAILED:<BR>{}<BR>'.format(bmarks_sql)
        return return_data
    bmarks_qry_all_res = db_qry([bmarks_sql_all, None], 'select')
    if not bmarks_qry_all_res:
        return_data += '<span class="bad">Bmarks All query FAILED<BR>{}<BR>'.format(bmarks_sql_all)
        return return_data
    num_bmarks_all = len(bmarks_qry_all_res)
    num_bmarks = len(bmarks_qry)
    if num_bmarks:
        return_data += '<TABLE><TR><TD>{b}</TD>'.format(b=bmarks_intro)
        # only render the bmarks/page menu on the 'MY BOOKMARKS' page
        if num_bmarks_menu_offset == default_num_bmarks_menu_offset:
            return_data += '''<TD width="{n}%">&nbsp;</TD><TD align="center" valign="top"><div id="menu">
                                <UL id="item1">
                                <LI class="top"><B>Bookmarks/page</B></LI>
                                        <LI class="item"><A HREF="{u}num=5">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a5}5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=10">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a10}10&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=15">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a15}15&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a20}20&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=30">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a30}30&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI></UL>
                                </DIV>&nbsp;</TD>'''.format(n=num_bmarks_menu_offset,
                                                            u=url_get_base,
                                                            a5=marker_dict['5'],
                                                            a10=marker_dict['10'],
                                                            a15=marker_dict['15'],
                                                            a20=marker_dict['20'],
                                                            a30=marker_dict['30'])
        return_data += '</TR></TABLE>'
        for bmark_row in bmarks_qry:
            notes_string = ''
            url = bmark_row[0]
            bm_id = bmark_row[1]
            last_update = bmark_row[2]
            notes = bmark_row[3].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
            name = bmark_row[4].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
            owner = bmark_row[5]
            tags_sql = "SELECT tag FROM bmarks WHERE url='{u}' ".format(u=url)
            if hash_check() and request.query.get('whose') and request.query.get('whose') == mine:
                tags_sql += "AND owner='{u}' ".format(u=username)
                bmark_user_edit_string = '''<BR><A HREF="edit?id={i}&func=edit"><span class="normal"><B>EDIT</B></a>
                                            &nbsp;|&nbsp;<A HREF="{h}bmarks?id={i}&func=del"><B>DELETE</B></a>&nbsp;</span>'''.format(i=bm_id,
                                                                                                                                      h=base_url)
            else:
                bmark_user_edit_string = '''<BR><span class="normal">Created by <A HREF="{h}bmarks?whose={o}">
                                            <B>{o}</B></a>&nbsp;</span>'''.format(o=owner,
                                                                                  h=base_url)
            tags_sql += 'AND length(tag)>0 GROUP BY tag ORDER BY tag LIMIT 15'
            tags_qry = db_qry([tags_sql, None], 'select')
            if notes:
                notes_string = '<BR><span class="small"><B>{n}</B></span>'.format(n=notes)
            return_data += '''<TABLE><TR><TD valign="top"><span class="big">{l}&nbsp;&nbsp;&nbsp;</span></TD>
                                <TD width="65%"><span class="big"><A HREF="{u}">{n}</a></span>
                                {no}{b}</TD>'''.format(l=last_update, u=url, n=name,
                                                       no=notes_string, b=bmark_user_edit_string)
            num_tags = len(tags_qry)
            if num_tags:
                return_data += '<TD width="95%" valign="top" align="right">'
                tag_counter = 0
                for tag_row in tags_qry:
                    tag = tag_row[0]
                    tag_sql = "SELECT id FROM tags WHERE tag='{t}' ".format(t=tag)
                    if hash_check() and request.query.get('whose'):
                        tag_sql += "AND owner='{u}'".format(u=username)
                    tag_sql += 'ORDER BY id LIMIT 1'
                    tag_qry_res = db_qry([tag_sql, None], 'select')
                    if not tag_qry_res:
                        return_data += '<span class="bad">Tags query FAILED:<BR>{}<BR>'.format(tags_sql)
                        return
                    tag_id = tag_qry_res[0][0]
                    return_data += '<A HREF="{h}tags?id={tid}">{t}</a>&nbsp;&nbsp;'.format(tid=tag_id,
                                                                                           t=tag,
                                                                                           h=base_url)
                    tag_counter += 1
                    if tag_counter > 4:
                        tag_counter = 0
                        return_data += '<BR>'
                return_data += '&nbsp;</TD>'
            return_data += '</TR></TABLE><HR><BR>'
        # pagination settings
        my_row_count = num_bmarks_all
        total_pages = ceil(int(my_row_count) / int(max_results))
        pagination = ''

        # Create a PREV link if one is needed
        if page > 1:
            pagination += '''<A STYLE="text-decoration:none" title="PREVIOUS PAGE" HREF="{h}bmarks?whose={w}&page={p}&num={u}">
                             <span class="huge"><H1>&larr;</H1></span></A>'''.format(w=whose,
                                                                                     p=prev,
                                                                                     u=user_num_bmarks,
                                                                                     h=base_url)
        if not request.query.get('whose'):
            page = 0
            total_pages = 0
        # Create a NEXT link if one is needed
        if page < total_pages:
            pagination += '''<A STYLE="text-decoration:none" title="NEXT PAGE" HREF="{h}bmarks?whose={w}&page={n}&num={u}">
                             <span class="huge"><H1>&rarr;</H1></span></A>'''.format(w=whose, n=next, u=user_num_bmarks,
                                                                                     h=base_url)
        else:
            # adjust the total count when on the last page since
            # it might not have user_num_bmarks items remaining
            new_max_results = (int(max_results) - ((int(page) * int(max_results)) - int(my_row_count)))
            max_results = new_max_results
        plural = ''
        if my_row_count:
            plural = 's'
        return_data += '''<TABLE width="100%"><TR COLSPAN="1"><TD>&nbsp;</TD></TR>
                          <TR><TD COLSPAN="9">&nbsp;{m} Tasti bookmark{p}</TD>
                          <TD class="page" COLSPAN="4"><B>{pa}</B></TD></TR></TABLE><BR>'''.format(m=my_row_count,
                                                                                                   p=plural,
                                                                                                   pa=pagination)
    else:
        return_data += '<BR>There are currently no bookmarks<BR><BR>'
    return return_data


def footer():
    """Footer content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    year = year = datetime.date.today().year
    return_data = '''<span class="footer_class1">
<CENTER><A HREF="{h}">HOME</a>&nbsp;<BR><A HREF="https://github.com/netllama/tasti">Tasti</a> is licensed under the <A HREF="http://www.gnu.org/licenses/gpl.html">GPL</a>.  Copyright {y}<BR>
</CENTER></span>'''.format(y=year, h=base_url)
    return return_data


def auth_check():
    """Check whether user is authenticated."""
    payload = {'is_authenticated': False, 'username': None}
    if request.get_cookie('tasti_username') and hash_check():
        payload['is_authenticated'] = True
        username = request.get_cookie('tasti_username').lower()
        payload['username'] = username
    return payload


def hash_check():
    """Validate password hash."""
    username = ''
    password_hash = ''
    if request.get_cookie('tasti_username'):
        username = request.get_cookie('tasti_username')
    if request.get_cookie('tasti_hash'):
        password_hash = request.get_cookie('tasti_hash')

    hash_sql = "SELECT id FROM users WHERE username='{u}' AND password='{p}'".format(u=username, p=password_hash)
    hash_qry = db_qry([hash_sql, None], 'select')
    if len(hash_qry) and hash_qry[0]:
        return hash_qry


def db_qry(sql_pl, operation):
    """Run specified query."""
    ret_val = True
    sql = sql_pl[0]
    sql_vals = sql_pl[1]
    # connect to database
    try:
        conn = psycopg2.connect(CONN_STRING)
        conn.autocommit = True
    except Exception as err:
        print 'Database connection failed due to error:\t{}'.format(err)
        return False
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # invoke the SQL
    try:
        cursor.execute(sql, sql_vals)
        row_count = cursor.rowcount
    except Exception as err:
        # query failed
        print 'SQL ( {} )\t failed due to error:\t{}'.format(cursor.query, err)
        ret_val = False
    if operation == 'select' and ret_val:
        # get returned data to return
        ret_val = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret_val
