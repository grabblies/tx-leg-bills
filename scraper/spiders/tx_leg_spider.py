import scrapy
import bs4 as soup


class BillSpider(scrapy.Spider):
    name = "bills"

    sample_search = 'https://capitol.texas.gov/Search/BillSearchResults.aspx?NSP=1&SPL=True&SPC=False&SPA=False&SPS=False&Leg=86&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;CR;R;;;&AuthorCode=A2155&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=&AAO=&Subjects=&SAO=&TT=&ID=AoSGWUnvX'
    blank_search = 'https://capitol.texas.gov/Search/BillSearchResults.aspx?NSP=1&SPL=True&SPC=False&SPA=False&SPS=False&Leg={0}&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;CR;R;;;&AuthorCode={1}&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=&AAO=&Subjects=&SAO=&TT=&ID=AoSGWUnvX'

    def start_requests(self):
        starting_site = "https://capitol.texas.gov/Search/BillSearch.aspx"
        request = scrapy.Request(starting_site, method="POST", callback=self.parse_sessions)

        return [request]

    def parse_sessions(self, starting_response):
        list_of_leg_sessions = starting_response.xpath('//select[@name="cboLegSess"]/option/@value').getall()
        print(list_of_leg_sessions)

        for session in list_of_leg_sessions[0:1]:
            print("should be this session: " + session)
            form_request = scrapy.FormRequest.from_response(starting_response,
                                                   formname='cboLegSess',
                                                   method='GET',
                                                   formdata={'selected': session,
                                                             'cboLegSess': session,
                                                             'LegSess': session},
                                                   callback=self.parse_authors_for_session,
                                                   dont_click=True,
                                                   meta={"sample_response": starting_response})
            yield form_request


    def parse_authors_for_session(self, form_response):

        selected_session = form_response.xpath('//select[@name="cboLegSess"]/option[@selected="selected"]/@value').get()
        print("selected session: " + str(selected_session))

        filler_response = form_response.meta["sample_response"]

        list_of_authors_in_session = filler_response.xpath('//select[@name="usrLegislatorsFolder$cboAuthor"]/option/@value').getall()

        print("list of authors in session", list_of_authors_in_session)

        for author in list_of_authors_in_session[0:2]:
            if len(author) == 0:
                pass

            print("this author: " + author)
            search_url = self.blank_search.format(selected_session, author)

            print (search_url)

            yield scrapy.Request(url=search_url, callback=self.parse)

    def parse_list_of_bills(self, response):

        bill_relative_urls = response.xpath('//a[@name="startcontent"]/following::table//a[@target="_new"]/@href').getall()

        domain = "https://capitol.texas.gov/"
        bill_absolute_urls = [x.replace("..", domain) for x in bill_relative_urls]

        for url in bill_absolute_urls:
            yield scrapy.Request(url=url, callback=self.parse_bill_page)
        print("THIS IS THE RESPONSE")
        # print(response)


    def parse_bill_page(self, response):

