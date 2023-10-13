function oneTime() { 
    let spans = document.getElementsByTagName('span');
    for (let i = 0; i < spans.length; i++) { 
        let txt = spans[i].innerText; 

        if (txt == 'You have completed this exercise') { 
            if ( spans[i].parentElement.className == 'alert alert-success alert-exercise-completed ng-scope' ) { 
                let btns = document.getElementsByTagName('button');
                for (let i = 0; i < btns.length; i++) { 
                    if ( btns[i].innerText.includes( 'Page:' ) ) {
                        btns[i + 1].click();
                        return 
                    }
                }
            }
        
            if ( spans[i].parentElement.className == 'alert alert-success alert-exercise-completed ng-scope ng-hide' ) {
         
                let btns = document.getElementsByTagName('button'); 
                for (let i = 0; i < btns.length; i++) { 
                    let txt = btns[i].innerText; 
         
                    if (txt == 'RUN') {  
                        btns[i].click(); 
                        
                        setTimeout(function(){ 
                            
                            var btns2 = document.getElementsByTagName('button'); 
                            
                            for (let j = 0; j < btns2.length; j++) { 
                                let txt = btns2[j].innerText; 
                                if (txt == 'Submit') {
                                    setTimeout(function(){  
                                        btns2[j].click(); 
                                        console.log( 'Submitted!' ); 
                                    }, 2500)
                                }    
                            } 
                        }, 2500);
                    };
                } 
            }; 
        } 
    }
}

oneTime()