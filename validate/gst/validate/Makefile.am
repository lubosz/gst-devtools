libgstvalidate_@GST_API_VERSION@_la_SOURCES = \
	gst-validate-runner.c \
	gst-validate-reporter.c \
	gst-validate-monitor.c \
	gst-validate-element-monitor.c \
	gst-validate-bin-monitor.c \
	gst-validate-pad-monitor.c \
	gst-validate-monitor-factory.c \
	gst-validate-report.c \
	gst-validate-scenario.c \
	gst-validate-override.c \
	gst-validate-utils.c \
	gst-validate-override-registry.c \
	media-descriptor.c \
	media-descriptor-writer.c \
	media-descriptor-parser.c \
	gst-validate-media-info.c \
    validate.c

libgstvalidate_@GST_API_VERSION@include_HEADERS = \
    validate.h \
	gettext.h \
	gst-validate-bin-monitor.h \
	gst-validate-element-monitor.h \
	gst-validate-i18n-lib.h \
	gst-validate-internal.h \
	gst-validate-monitor-factory.h \
	gst-validate-monitor.h \
	gst-validate-override.h \
	gst-validate-override-registry.h \
	gst-validate-pad-monitor.h \
	gst-validate-reporter.h \
	gst-validate-report.h \
	gst-validate-runner.h \
	gst-validate-scenario.h \
	gst-validate-utils.h \
	media-descriptor.h \
	media-descriptor-writer.h \
	media-descriptor-parser.h \
	gst-validate-media-info.h


lib_LTLIBRARIES = libgstvalidate-@GST_API_VERSION@.la

if HAVE_LD_PRELOAD
lib_LTLIBRARIES += libgstvalidate-default-overrides-@GST_API_VERSION@.la \
	libgstvalidate-preload-@GST_API_VERSION@.la
endif

libgstvalidate_@GST_API_VERSION@_la_CFLAGS = $(GST_ALL_CFLAGS) $(GIO_CFLAGS) $(GST_PBUTILS_CFLAGS)
libgstvalidate_@GST_API_VERSION@_la_LDFLAGS = $(GST_LIB_LDFLAGS) $(GST_ALL_LDFLAGS) \
	$(GST_LT_LDFLAGS) $(GIO_LDFLAGS) $(GST_PBUTILS_LDFAGS)
libgstvalidate_@GST_API_VERSION@_la_LIBADD = \
	$(GST_PLUGINS_BASE_LIBS) $(GST_BASE_LIBS) \
	$(GST_ALL_LIBS) $(GIO_LIBS) $(GST_PBUTILS_LIBS)

libgstvalidate_@GST_API_VERSION@includedir = $(includedir)/gstreamer-@GST_API_VERSION@/gst/validate

if HAVE_LD_PRELOAD
libgstvalidate_default_overrides_@GST_API_VERSION@_la_SOURCES = \
    gst-validate-default-overrides.c

libgstvalidate_default_overrides_@GST_API_VERSION@_la_CFLAGS = $(GST_ALL_CFLAGS) $(GIO_CFLAGS)
libgstvalidate_default_overrides_@GST_API_VERSION@_la_LDFLAGS = $(GST_LIB_LDFLAGS) $(GST_ALL_LDFLAGS) \
	$(GST_LT_LDFLAGS) $(GIO_LDFLAGS)
libgstvalidate_default_overrides_@GST_API_VERSION@_la_LIBADD = \
	$(GST_PLUGINS_BASE_LIBS) $(GST_BASE_LIBS) \
	$(GST_ALL_LIBS) $(GIO_LIBS)

libgstvalidate_default_overrides_@GST_API_VERSION@includedir = $(includedir)/gstreamer-@GST_API_VERSION@/gst/validate
libgstvalidate_default_overrides_@GST_API_VERSION@include_HEADERS =

libgstvalidate_preload_@GST_API_VERSION@_la_SOURCES = \
	gst-validate-monitor-preload.c

libgstvalidate_preload_@GST_API_VERSION@_la_CFLAGS = $(GST_ALL_CFLAGS)
libgstvalidate_preload_@GST_API_VERSION@_la_LDFLAGS =  $(GST_LIB_LDFLAGS) $(GST_ALL_LDFLAGS) \
	$(GST_LT_LDFLAGS)
libgstvalidate_preload_@GST_API_VERSION@_la_LIBADD =  \
	$(GST_PLUGINS_BASE_LIBS) $(GST_BASE_LIBS) \
	$(GST_ALL_LIBS)
libgstvalidate_preload_@GST_API_VERSION@includedir = $(includedir)/gstreamer-@GST_API_VERSION@/gst/validate
libgstvalidate_preload_@GST_API_VERSION@include_HEADERS =
endif

#AM_CFLAGS = $(GST_ALL_CFLAGS) $(GST_PBUTILS_CFLAGS)
#LDADD = $(top_builddir)/gst/validate/libgstvalidate-@GST_API_VERSION@.la $(GST_PBUTILS_LIBS) $(GST_LIBS)

CLEANFILES =
