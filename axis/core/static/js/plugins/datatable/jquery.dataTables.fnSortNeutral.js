// http://datatables.net/plug-ins/api#fnSortNeutral

$.fn.dataTableExt.oApi.fnSortNeutral = function ( oSettings )
{
    /* Remove any current sorting */
    oSettings.aaSorting = [];

    /* Sort display arrays so we get them in numerical order */
    oSettings.aiDisplay.sort( function (x,y) {
        return x-y;
    } );
    oSettings.aiDisplayMaster.sort( function (x,y) {
        return x-y;
    } );

    oSettings.oPreviousSearch.sSearch = "";

    /* Redraw */
    oSettings.oApi._fnReDraw( oSettings );
};
